using EnerdeqExportFromQuery.Utility;
using IHS.EnergyWebServices.ExportFromQuerySample.Services;
using IHSEnergy.Enerdeq.ExportBuilder;
using IHSEnergy.Enerdeq.QueryBuilder;
using IHSEnergy.Enerdeq.Session;
using System;
using System.Configuration;
using System.IO;
using System.Linq;

namespace IHS.EnergyWebServices.ExportFromQuerySample.Export.ExportStrategy
{
    /// <summary>
    /// Exports data using criteriaXml file.
    /// </summary>
    public class CriteriaXmlExportStrategy : IExportStrategy
    {
        /// <summary>
        /// Exports data
        /// </summary>
        /// <param name="session">Active Enerdeq Web Service session</param>
        /// <param name="options">Export parameters</param>
        public void Export(WebServicesSession session, Options options)
        {
            var queryString = string.Empty;
            try
            {
                queryString = File.ReadAllText(options.Query);
                queryString = queryString.Trim();
            }
            catch
            {
                throw new IOException("Unable to read criteriaXml file.");
            }

            var query = string.Empty;
            using (var queryBuilder = new QueryBuilder(session))
            {
                if (!string.IsNullOrWhiteSpace(options.LastUpdateDate))
                {
                    DateTime oDate;
                    string[] formats = { "yyyy/MM/dd" };
                    if (DateTime.TryParseExact(options.LastUpdateDate,
                        formats,
                        System.Globalization.CultureInfo.InvariantCulture,
                        System.Globalization.DateTimeStyles.None,
                        out oDate))
                    {
                        var queryObect = CriteriaService.CreateQueryObject(queryString);

                        var valueId = 0;
                        var criteria = CriteriaService.GetAllCriteria(queryObect);
                        if (criteria.IsNullorEmpty()) throw new ArgumentException("Query contains no criteria.");

                        valueId = criteria.Count();
                        if (options.Datatype.IsNullorEmpty()) options.Datatype = CriteriaService.GetCriteriaDataType(criteria.First());
                        var attribute = options.Datatype.ToLower().Contains("production") ? "Last Update" : "Last Activity Date";

                        var search = new CriteriaService.CriteriaSearch();
                        search.Domain = options.Domain; ;
                        search.Datatype = options.Datatype;
                        search.AttributeGroup = "Date";
                        search.Attribute = attribute;

                        var lastUpdateCriteria = CriteriaService.GetCriteria(queryObect, search);
                        if (lastUpdateCriteria == null)
                        {
                            var newCriteria = CriteriaService.CreateLastUpdateCriteria(valueId.ToString(), options.Datatype, attribute, CriteriaService.FilterLogic.GreaterThanOrEquals, oDate, options.Domain);
                            CriteriaService.AddCriteria(queryObect, newCriteria);
                        }
                        else
                        {
                            var newCriteria = CriteriaService.CreateLastUpdateCriteria((valueId - 1).ToString(), options.Datatype, attribute, CriteriaService.FilterLogic.GreaterThanOrEquals, oDate, options.Domain);
                            CriteriaService.ReplaceCriteria(queryObect, search, newCriteria);
                        }
                        query = queryObect.ToString();
                    }
                    else
                    {
                        throw new ArgumentException("Last Update Date is invalid.");
                    }
                }
                else
                {
                    query = queryString;
                }

                var count = queryBuilder.GetCount(query);
                if (options.Verbose) Console.WriteLine("Query results in {0} items.", count);

                using (var exportBuilder = new ExportBuilder(session))
                {
                    var datatype = EwsUtility.GetDatatypeFromQuery(queryBuilder, query);

                    //  If count is over 5000 use the ExportBuilder to get the id list
                    string[] ids = count <= 5000 ? queryBuilder.GetKeys(query) : EwsUtility.GetIdList(exportBuilder, datatype, query,options.Domain ,options.Verbose);

                    //  Chunk the list of ids to something reasonable
                    int chunkSize = 0;
                    if (!int.TryParse(ConfigurationManager.AppSettings["ChunkSize"], out chunkSize))
                    {
                        throw new ArgumentException("ChunkSize is not a valid integer.");
                    }
                    var chunks = ids.Chunk(chunkSize);

                    foreach (var chunk in chunks)
                    {
                        var filename = string.Format("{0}", Guid.NewGuid());
                        var jobid = string.Empty;
                        var buildStandardFlag = options.TemplateType.ToLower().Contains("standard");

                        if (buildStandardFlag)
                        {
                            //  Build standard export
                            jobid = exportBuilder.Build(options.Domain, datatype, options.TemplateName, chunk.ToArray(), filename, Overwrite.True);
                        }
                        else
                        {
                            //  Build oneline export
                            jobid = exportBuilder.BuildOneline(options.Domain, datatype, chunk.ToArray(), options.TemplateName, options.FileType, filename, Overwrite.True);
                        }


                        //  Store file in temp directory
                        var tempFilename = Path.Combine(options.WorkingDirectory, jobid);
                        EwsUtility.RetrieveFile(exportBuilder, jobid, tempFilename, options.Verbose);

                        if (options.Verbose) Console.Out.WriteLine("File '{0}' created.", tempFilename);
                    }
                }
            }
        }
    }
}
