using IHSEnergy.Enerdeq.ExportBuilder;
using IHSEnergy.Enerdeq.QueryBuilder;
using IHSEnergy.Enerdeq.ReportBuilder;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;
using System.Xml;
using System.Configuration;

namespace EnerdeqExportFromQuery.Utility
{
    /// <summary>
    /// Utility class for Enerdeq Web Services.
    /// </summary>
    public class EwsUtility
    {
        public static string GetDatatypeFromQuery(QueryBuilder qb, string query)
        {
            string queryText = query;
            if (qb.GetSavedQueries().Contains(query))
            {
                queryText = qb.GetQueryDefinition(query);
            }

            var doc = new XmlDocument();
            doc.LoadXml(queryText);
            var datatypenode = doc.SelectSingleNode("/criterias/criteria/datatype");
            return datatypenode.InnerText;

        }

        public static string RetrieveFile(ExportBuilder eb, string jobid, string fileName, bool verbose)
        {

            int maxretry = Int32.Parse(ConfigurationManager.AppSettings["MaxRetryTime"]); 
            var retry = 0;
            while (!eb.IsComplete(jobid) && retry++ < maxretry)
            {
                Task.Delay(1000).Wait();
            }

            if (verbose) Console.WriteLine("Pinged for completion {0} times", retry);
            if (retry >= maxretry) throw new Exception("Export didn't build in time.");

            Task.Delay(5000).Wait();
            retry = 0;
            while (!eb.Exists((jobid)) && retry++ < 30)
            {
                Task.Delay(1000).Wait();
            }

            if (!eb.Exists(jobid)) throw new Exception("File does not exist.");

            var bytes = eb.Retrieve(jobid, true);
            eb.Delete(jobid);
            var path = Path.GetDirectoryName(fileName);
            if (path != null && !Directory.Exists(path)) Directory.CreateDirectory(path);

            File.WriteAllBytes(fileName, bytes);
            return fileName;

        }

        public static string RetrieveReport(ReportBuilder rb, string jobid, string fileName, bool verbose = true)
        {

            int maxretry = Int32.Parse(ConfigurationManager.AppSettings["MaxRetryTime"]);
            var retry = 0;
            while (!rb.IsComplete(jobid) && retry++ < maxretry)
            {
                Task.Delay(1000).Wait();
            }

            if (verbose) Console.WriteLine("Pinged for completion {0} times", retry);
            if (retry >= maxretry) throw new Exception("Report didn't build in time.");

            Task.Delay(5000).Wait();
            retry = 0;
            while (!rb.Exists((jobid)) && retry++ < 30)
            {
                Task.Delay(1000).Wait();
            }

            if (!rb.Exists(jobid)) throw new Exception("File does not exist.");

            var bytes = rb.Retrieve(jobid, true);
            rb.Delete(jobid);
            var path = Path.GetDirectoryName(fileName);
            if (path != null && !Directory.Exists(path)) Directory.CreateDirectory(path);

            File.WriteAllBytes(fileName, bytes);
            return fileName;

        }

        public static string[] GetIdList(ExportBuilder eb, string datatype, string query, string domain, bool verbose = true)
        {
            string idListTemplate = GetIdListTemplateName(datatype);

            string jobid = eb.BuildFromQuery(domain, datatype, idListTemplate, query, Guid.NewGuid().ToString(),
                Overwrite.True);

            var tempfilename = RetrieveFile(eb, jobid, Path.GetTempFileName(), verbose);

            var ids = File.ReadAllLines(tempfilename);
            File.Delete(tempfilename);
            return ids;

        }

        public static string GetIdListTemplateName(string datatype)
        {
            if (string.IsNullOrEmpty(datatype)) throw new ArgumentNullException("datatype");
            if (datatype.Equals("Well", StringComparison.CurrentCultureIgnoreCase)) return "Well Id List";
            if (datatype.Equals("Activity", StringComparison.CurrentCultureIgnoreCase)) return "Well Id List";
            if (datatype.Equals("Activity Data", StringComparison.CurrentCultureIgnoreCase)) return "Well Id List";
            if (datatype.Equals("Production Allocated", StringComparison.CurrentCultureIgnoreCase))
                return "Production Id List";
            if (datatype.Equals("Production Unallocated", StringComparison.CurrentCultureIgnoreCase))
                return "Production Id List";

            throw new ArgumentException(string.Format("'{0}' is an unrecognized datatype value.", datatype), datatype);

        }

        public static string GetUpdatedSinceQuery(string datatype, string updatedSinceDate)
        {
            var query = File.ReadAllText(@"Queries\UpdatedSinceQuery.xml");
            query = query.Replace("$DATATYPE$", datatype);
            query = query.Replace("$UPDATEDSINCEDATE$", updatedSinceDate);
            return query;
        }

        public static string GetDateQuery(string datatype, string fromDate, string domain, string attribute = "Last Update")
        {
            var query = "<criterias><criteria type=\"value\"><domain>$DOMAIN$</domain><datatype>$DATATYPE$</datatype><attribute_group>Date</attribute_group><attribute>$ATTRIBUTE$</attribute><type>date</type><displaytype /><filter logic=\"greater_than_or_equals\"><value actual=\"$FROMDATE$\" /></filter></criteria></criterias>";

            query = query.Replace("$DATATYPE$", datatype);
            query = query.Replace("$ATTRIBUTE$", attribute);
            query = query.Replace("$FROMDATE$", fromDate);
            query = query.Replace("$DOMAIN$", domain);
            return query;
        }

        public static string GetValue(string[] args, int index, string defaultValue)
        {
            return args.Length > index ? args[index] : defaultValue;
        }

        public static List<string> DeleteAllExports(ExportBuilder eb, string startsWith)
        {

            // Get a list of all jobs
            var jobs = eb.List().ToList();

            // Remove all that don't startWith provide string
            if (!string.IsNullOrEmpty(startsWith))
                jobs.RemoveAll((x) => !x.StartsWith(startsWith));

            // Delete remaining jobs
            foreach (var job in jobs)
            {
                eb.Delete(job);
            }

            return jobs;
        }
    }
}