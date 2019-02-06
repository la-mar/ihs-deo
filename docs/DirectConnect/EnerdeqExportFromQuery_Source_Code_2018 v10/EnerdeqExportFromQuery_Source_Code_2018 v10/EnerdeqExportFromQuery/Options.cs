using CommandLine;
using CommandLine.Text;
using System;
using System.Configuration;
using System.IO;
using System.Collections.Generic;

namespace IHS.EnergyWebServices.ExportFromQuerySample
{
    /// <summary>
    /// Default options for export.
    /// </summary>
    public static class DefaultOptions
    {
        public static readonly string Filetype = "Comma Separated";
        public static readonly string TemplateName = "Well Header List";
        public static readonly string TemplateType = "Standard";
        public static readonly string WorkingDirectory = Path.GetFullPath(Path.GetTempPath());
        public static readonly string Url = "https://webservices.ihsenergy.com/WebServices/";
        //public static readonly IList <string> SpatialExports = new[] { " " };
        public static readonly IList<string> SpatialExports = new List<string>(new string[] { " " });
        public static readonly string SpatialFormat = " ";
        public static readonly string SpatialExtent = "(-90,90),(-180,180)";
        public static readonly Nullable<bool> SpatialExportOverWrite = true;
        public static readonly String SpatialTileSize = "1X1";
        public static readonly string Domain = "US";
    }

    /// <summary>
    /// Parameters set for exports.
    /// </summary>
    public class Options
    {
        [Option('u', "username", HelpText = "Required. IHS Enerdeq / Energy Web Services username.")]
        public string Username { get; set; }

        [Option('p', "password", HelpText = "Required. IHS Enerdeq / Energy Web Services password.")]
        public string Password { get; set; }

        [Option('n', "templateName", HelpText = "(Default: Well Header List) The name of the template to use.")]
        public string TemplateName { get; set; }

        [Option('t', "templateType", HelpText = "(Default: Standard) The type of template (Standard or Oneline)")]
        public string TemplateType { get; set; }

        [Option('q', "query", HelpText = "Required. The saved query name, criteriaXML file, or Ids file to use.")]
        public string Query { get; set; }

        [Option('s', "lastUpdateDate", HelpText ="Adds Last Update Date critiera to query. (Format: yyyy/MM/dd)")]
        public string LastUpdateDate { get; set; }

        [Option('d', "Datatype", HelpText = "Well, Production Allocated, or Production Unallocated (Required if using Ids file).")]
        public string Datatype { get; set; }

        [Option('f', "filetype", HelpText = "(Default: Comma Separated) The file type to create. One of Comma Separated, Tab Delimited, HTML, Comma Separated, Excel.")]
        public string FileType { get; set; }

        [Option('l', "url", HelpText = "(Default: https://webservices.ihsenergy.com/WebServices/)The base url for the services to connect to.")]
        public string Url { get; set; }

        [Option('w', "workingDirectory", HelpText = "The base directory to download files to.")]
        public string WorkingDirectory { get; set; }


        [Option('v', "verbose", DefaultValue = false, HelpText = "Prints all messages to standard output.")]
        public bool Verbose { get; set; }

        [OptionList('x', "spatialExports", Separator=',', HelpText = "Optional. IHS Enerdeq / Energy Web Services spatial export.")]
        public IList<string> SpatialExports { get; set; }
        
        [Option('o', "spatialFormat", HelpText = "Optional. IHS Enerdeq / Energy Web Services spatial export format.")]
        public string SpatialFormat { get; set; }

        [Option('e', "spatialExtent", HelpText = "Optional. IHS Enerdeq / Energy Web Services spatial export extent((-120,-119)(35,36))")]
        public string SpatialExtent { get; set; }

        [Option('r', "spatialExportOverWrite", DefaultValue = true, HelpText = "Set Spatial Export Overwrite value (default=true).")]
        public Nullable<bool> SpatialExportOverWrite { get; set; }


        [Option('i', "spatialTileSize", HelpText = "Set Spatial Tile Size value (default= 1X1 ).")]
        public string SpatialTileSize { get; set; }

        [Option('m', "domain", HelpText = "Domain for the services to connect to (default= US ).")]
        public string Domain { get; set; }

        [HelpOption]
        public string GetUsage()
        {
            return HelpText.AutoBuild(this,
              (HelpText current) => HelpText.DefaultParsingErrorsHandler(this, current));
        }

        /// <summary>
        /// Creates Options object with values set to default values from configuration file.
        /// </summary>
        public Options()
        {
            Username = ConfigurationManager.AppSettings["Username"];
            Password = ConfigurationManager.AppSettings["Password"];
            TemplateName = ConfigurationManager.AppSettings["TemplateName"];
            TemplateType = ConfigurationManager.AppSettings["TemplateType"];
            Query = ConfigurationManager.AppSettings["Query"];
            LastUpdateDate = ConfigurationManager.AppSettings["LastUpdateDate"];
            Datatype = ConfigurationManager.AppSettings["Datatype"];
            FileType = ConfigurationManager.AppSettings["FileType"];
            Url = ConfigurationManager.AppSettings["Url"];
            var dir = ConfigurationManager.AppSettings["WorkingDirectory"];
            Domain = ConfigurationManager.AppSettings["Domain"];
            if (!string.IsNullOrWhiteSpace(dir))
            {
                // WorkingDirectory = Path.GetFullPath(Path.Combine(dir, string.Format("{0:yyyy-MM-dd_HH-mm}", DateTime.Now)));
                WorkingDirectory = Path.GetFullPath(dir);
            }
            else
            {
               //WorkingDirectory = Path.GetFullPath(Path.Combine(DefaultOptions.WorkingDirectory, string.Format("{0:yyyy-MM-dd_HH-mm}", DateTime.Now)));
                WorkingDirectory = Path.GetFullPath(DefaultOptions.WorkingDirectory);
            }

            //SpatialExports = new[] { ConfigurationManager.AppSettings["SpatialExports"] };
            SpatialExports = new List<string> (ConfigurationManager.AppSettings["SpatialExports"].Split(new char[] { ',' }));
            if (SpatialExports.Count <= 0)
            {
                //SpatialExports = new[] { " " };
                SpatialExports = new List<string>(new string[] {" "});
            }

            SpatialFormat = ConfigurationManager.AppSettings["SpatialFormat"];
            if (string.IsNullOrWhiteSpace(SpatialFormat))
            {
                SpatialFormat = " ";
            }


            SpatialExtent = ConfigurationManager.AppSettings["SpatialExtent"];
            if (string.IsNullOrWhiteSpace(SpatialExtent))
            {
                SpatialExtent = "(-120,-119)(35,36)";
            }
            SpatialTileSize = ConfigurationManager.AppSettings["SpatialTileSize"];
            if (string.IsNullOrWhiteSpace(SpatialTileSize))
            {
                SpatialTileSize = "1X1";
            }

        }
    }
}
