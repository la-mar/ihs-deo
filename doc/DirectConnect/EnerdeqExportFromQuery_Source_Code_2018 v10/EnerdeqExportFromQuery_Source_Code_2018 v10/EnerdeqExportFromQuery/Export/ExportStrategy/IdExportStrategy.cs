using EnerdeqExportFromQuery.Utility;
using IHSEnergy.Enerdeq.ExportBuilder;
using IHSEnergy.Enerdeq.QueryBuilder;
using IHSEnergy.Enerdeq.Session;
using System;
using System.Collections.Generic;
using System.Configuration;
using System.IO;
using System.Linq;

namespace IHS.EnergyWebServices.ExportFromQuerySample.Export.ExportStrategy
{
    /// <summary>
    /// Exports data using Ids file.
    /// </summary>
    public class IdExportStrategy : IExportStrategy
    {
        /// <summary>
        /// Exports data
        /// </summary>
        /// <param name="session">Active Enerdeq Web Service session</param>
        /// <param name="options">Export parameters</param>
        public void Export(WebServicesSession session, Options options)
        {
            if (string.IsNullOrWhiteSpace(options.Datatype)) throw new ArgumentException("Datatype is required when using Ids file.");

            List<string> ids = new List<string>();
            try
            {
                var lines = File.ReadAllLines(options.Query);
                foreach (var line in lines)
                {
                    List<string> id = new List<string>();
                    if (line.Contains(','))
                    {
                        id = line.Split(',').Select(i => i.Trim()).Where(i => i != string.Empty).ToList();
                    }
                    else if (line.Contains(';'))
                    {
                        id = line.Split(';').Select(i => i.Trim()).Where(i => i != string.Empty).ToList();
                    }
                    else
                    {
                        id.Add(line.Trim());
                    }
                    ids.AddRange(id);
                }
            }
            catch
            {
                throw new IOException("Unable to read Ids file.");
            }

            using (var queryBuilder = new QueryBuilder(session))
            {
                var count = ids.Count();
                if (options.Verbose) Console.WriteLine("List contains {0} Ids.", count);

                using (var exportBuilder = new ExportBuilder(session))
                {
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
                            jobid = exportBuilder.Build(options.Domain, options.Datatype, options.TemplateName, chunk.ToArray(), filename, Overwrite.True);
                        }
                        else
                        {
                            //  Build oneline export
                            jobid = exportBuilder.BuildOneline(options.Domain, options.Datatype, chunk.ToArray(), options.TemplateName, options.FileType, filename, Overwrite.True);
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
