using IHS.EnergyWebServices.ExportFromQuerySample.Export;
using IHS.EnergyWebServices.ExportFromQuerySample.Export.ExportStrategy;
using IHS.EnergyWebServices.ExportFromQuerySample.Resources;
using IHSEnergy.Enerdeq.Session;
using System;
using System.Configuration;
using System.IO;
using System.Threading.Tasks;
using System.Text.RegularExpressions;

namespace IHS.EnergyWebServices.ExportFromQuerySample
{
    class Program
    {
        static void Main(string[] args)
        {
            try
            {
                //  Parse commandline parameters
                var options = new Options();
                if (!CommandLine.Parser.Default.ParseArguments(args, options))
                {
                    Task.Delay(8000).Wait();
                    //Console.ReadLine();
                    return;
                }

                options.TemplateName = correctTemplateValues(options.TemplateName);


                //  Validate required params
                if (string.IsNullOrWhiteSpace(options.Username) ||
                    string.IsNullOrWhiteSpace(options.Password)
                    && (string.IsNullOrWhiteSpace(options.Query) || string.IsNullOrWhiteSpace(options.SpatialExports.ToString())))
                {
                    Console.WriteLine("The following required parameters are missing:");
                    if (string.IsNullOrWhiteSpace(options.Username))
                    {
                        Console.WriteLine("\tusername");
                    }
                    if (string.IsNullOrWhiteSpace(options.Password))
                    {
                        Console.WriteLine("\tpassword");
                    }
                    Task.Delay(1000).Wait();
                    //Console.ReadLine();
                    return;
                }

                if (string.IsNullOrWhiteSpace(options.Domain))
                {
                    // Default to Production
                    options.Domain = DefaultOptions.Domain;
                    Console.WriteLine("Domain is missing, setting to US");
                }
                // Query Parameter
                if (!string.IsNullOrWhiteSpace(options.Query) && !string.IsNullOrWhiteSpace(options.SpatialExports[0]))
                {
                    Console.WriteLine("\t Please use either query(-q) or spatial export (-x)");
                    Task.Delay(1000).Wait();
                    //Console.ReadLine();
                    return;
                }

                 //  Validate App name
                if (string.IsNullOrWhiteSpace(ConfigurationManager.AppSettings["AppName"]))
                {
                    Console.WriteLine("AppName must be set in config.");
                    Task.Delay(1000).Wait();
                    //Console.ReadLine();
                    return;
                }
                // Validate URL
                if (string.IsNullOrWhiteSpace(options.Url))
                {
                    // Default to Production
                    options.Url = DefaultOptions.Url;
                    Console.WriteLine("URL is missing, setting to https://webservices.ihsenergy.com/WebServices/");
                }
                // Query Parameter
                if (!string.IsNullOrWhiteSpace(options.Query))
                {
                    //  Validate Last Update date format
                    if (!string.IsNullOrWhiteSpace(options.LastUpdateDate) &&
                        !IsValidDate(options.LastUpdateDate))
                    {
                        Console.WriteLine("Last Update Date is not valid. Date must be in the following format: yyyy/MM/dd.");
                        Task.Delay(1000).Wait();
                        //Console.ReadLine();
                        return;
                    }


                    if (string.IsNullOrEmpty(options.TemplateName))
                    {
                        // Default to Oneline Well Header List
                        options.TemplateName = DefaultOptions.TemplateName;
                        options.TemplateType = "Oneline";
                        Console.WriteLine("Template name is missing, setting to Well Header List, setting Template type to Oneline.");
                    }

                    if (string.IsNullOrWhiteSpace(options.TemplateType))
                    {
                        // Default to Standard template
                        options.TemplateType = DefaultOptions.TemplateType;
                        Console.WriteLine("Template type is missing, setting to Standard.");
                    }

                    if (string.IsNullOrWhiteSpace(options.FileType))
                    {
                        //  Default to comma separated
                        options.FileType = DefaultOptions.Filetype;
                        Console.WriteLine("Filetype is missing, setting to Comma Separated");
                    }

                    options.WorkingDirectory = Path.Combine(options.WorkingDirectory, "ExportFromQuery");
                    options.WorkingDirectory= Path.GetFullPath(Path.Combine(options.WorkingDirectory, string.Format("{0:yyyy-MM-dd_HH-mm}", DateTime.Now)));
                    Console.WriteLine("Working Directory setting to : " + options.WorkingDirectory);
                }
                //Spatial Exports flow
                else if (options.SpatialExports.Count>=1 &&  !string.IsNullOrWhiteSpace(options.SpatialExports[0]))
                {
                    if (string.IsNullOrWhiteSpace(options.SpatialExports.ToString()))
                    {
                        // Default to Production
                         options.SpatialExports = DefaultOptions.SpatialExports;
                    }

                    // Validate Spatial Extent
                    if (!IsValidExtent(options.SpatialExtent))
                    {
                        // Default to Production
                        options.SpatialExtent = DefaultOptions.SpatialExtent;
                        Console.WriteLine("Extent is missing/incorrect format, setting to (-120,-119)(35,36)");
                    }

                    // Validate Spatial Format
                    if (string.IsNullOrWhiteSpace(options.SpatialFormat))
                    {
                        // Default to Production
                        options.SpatialFormat = DefaultOptions.SpatialFormat;
                        Console.WriteLine("Format is missing, setting to blank");
                    }

                    if (!IsValidTileSize(options.SpatialTileSize))
                    {
                        // Default to SpatialTileSize
                        options.SpatialTileSize = DefaultOptions.SpatialTileSize;
                        Console.WriteLine("SpatialTileSize is missing, setting to 1 X 1 ");
                    }
                    // Validate Spatial Export Overwrite
                    if (!options.SpatialExportOverWrite.HasValue)
                    {
                        // Default to Production
                        options.SpatialExportOverWrite = DefaultOptions.SpatialExportOverWrite;
                        Console.WriteLine("Overwrite is missing, setting to true");
                    }

                    
                    options.WorkingDirectory = Path.Combine(options.WorkingDirectory, "SpatialExport");
                    options.WorkingDirectory = Path.GetFullPath(Path.Combine(options.WorkingDirectory, string.Format("{0:yyyy-MM-dd_HH-mm}", DateTime.Now)));
                    Console.WriteLine("Working Directory set to  : " + options.WorkingDirectory);
                }

                //  Connect to web service
                using (var session = WebServicesSession.Create(options.Url, options.Username, options.Password, ConfigurationManager.AppSettings["AppName"]))
                {
                    // Set up working directory
                    try
                    {
                        if (!Directory.Exists(options.WorkingDirectory)) Directory.CreateDirectory(options.WorkingDirectory);
                    }
                    catch (Exception ex)
                    {
                        Console.Error.WriteLine("\nERROR\nUnable to create working directory.\n{0}", ex.Message);
                        Task.Delay(1000).Wait();
                        //Console.ReadLine();
                        return;
                    }
                    if (options.Verbose)
                    {
                        Console.WriteLine("\nSuccessfully connected to Enerdeq Web Service");
                        Console.WriteLine("Working Directory: {0}\n", options.WorkingDirectory);
                        Console.WriteLine("URL: {0}", options.Url);
                        Console.WriteLine("Username: {0}", options.Username);
                        Console.WriteLine("Domain: {0}", options.Domain);
                        if (!string.IsNullOrWhiteSpace(options.Query))
                        { 
                            Console.WriteLine("Query: {0}", options.Query);
                            if (!string.IsNullOrWhiteSpace(options.LastUpdateDate)) Console.WriteLine("Last Update Date: {0}", options.LastUpdateDate);
                            if (!string.IsNullOrWhiteSpace(options.Datatype)) Console.WriteLine("Datatype: {0}", options.Datatype);
                            Console.WriteLine("Template Name: {0}", options.TemplateName);
                            Console.WriteLine("Template Type: {0}", options.TemplateType);
                            Console.WriteLine("Filetype: {0}", options.FileType);
                        }
                        else
                        {
                            Console.WriteLine("Spatial Exports (Layers): {0}", options.SpatialExports);
                            Console.WriteLine("Format: {0}", options.SpatialFormat);
                            Console.WriteLine("Extent: {0}", options.SpatialExtent);
                            Console.WriteLine("Spatial Tile Size: {0}", options.SpatialTileSize);
                        }
                        Task.Delay(10000).Wait();
                    }

                    ExportClient exportClient = new ExportClient(session);

                    //  Determine type of query
                    if (options.SpatialExports.Count >= 1 && !string.IsNullOrWhiteSpace(options.SpatialExports[0]))//spatial
                    {
                        exportClient.SetExportStrategy(new SpatialExportStrategy());
                    }
                    else
                    {
                        if (QueryTypes.GetQueryType(options.Query).Equals(QueryTypes.QueryType.CriteriaXml))
                        {
                            exportClient.SetExportStrategy(new CriteriaXmlExportStrategy());
                        }
                        else if (QueryTypes.GetQueryType(options.Query).Equals(QueryTypes.QueryType.Ids))
                        {
                            exportClient.SetExportStrategy(new IdExportStrategy());
                        }
                        else
                        {
                            exportClient.SetExportStrategy(new QueryNameExportStrategy());
                        }
                    }
                    //  Run export
                    exportClient.Export(options);
                   
                    if (options.Verbose)
                    {
                        Console.WriteLine("\nCompleted. Press any key to continue.");
                        Task.Delay(1000).Wait();
                        //Console.ReadLine();
                    }
                    else
                    {
                        Task.Delay(1000).Wait();
                        //Console.ReadLine();
                    }
                }
            }
            catch (Exception ex)
            {
                Console.Error.WriteLine("\n"+ ex.Message);
                Task.Delay(1000).Wait();
                //Console.ReadLine();
            }
        }

        /// <summary>
        /// Checks if date string is in valid format.
        /// </summary>
        /// <param name="date">Date string</param>
        /// <returns>True or false</returns>
        private static bool IsValidDate(string date)
        {
            if (string.IsNullOrWhiteSpace(date)) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            DateTime oDate;
            string[] formats = { "yyyy/MM/dd" };
            if (DateTime.TryParseExact(date,
                formats,
                System.Globalization.CultureInfo.InvariantCulture,
                System.Globalization.DateTimeStyles.None,
                out oDate)) return true;
            return false;
        }

        private static bool IsValidExtent(string extent)
        {
            if (string.IsNullOrWhiteSpace(extent)) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            var regex = @"^\(-?[0-9]*?.\d{1,10}\,-?[0-9]*?.\d{1,10}\)\(-?[0-9]*?.\d{1,10}\,-?[0-9]*?.\d{1,10}\)$";
            Match match = Regex.Match(extent, regex, RegexOptions.IgnoreCase);
            return (extent != string.Empty && match.Success);
          
        }
        private static bool IsValidTileSize(string tileSize)
        {
            if (string.IsNullOrWhiteSpace(tileSize)) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            tileSize = tileSize.ToUpper();
            var regex = @"^\d+X\d+$";
            Match match = Regex.Match(tileSize, regex, RegexOptions.IgnoreCase);
            return (tileSize != string.Empty && match.Success);
        }


        private static string correctTemplateValues(string templateValue)
        {
            char REPLACEMENTCHARACTER = '^';
            string EmptyString = "";

            string retValue = EmptyString;
            //All \r\]n and spaces cleaned
            templateValue = templateValue.Replace("\r", EmptyString);
            templateValue = templateValue.Replace("\n", EmptyString);
            //Replace single quotes and escape character (if any)
            templateValue = templateValue.Replace("'", EmptyString);
            templateValue = templateValue.Replace("\"", EmptyString);
            //Remove multiple spaces
            templateValue = System.Text.RegularExpressions.Regex.Replace(templateValue, @"\s+", " ");

            retValue = templateValue.Trim();

            string tempv = templateValue;
            char[] tempArr = new char[0];

            int index = 0;
            //Loop throught the complete string
            for (int i = 0; i < tempv.Length; i++)
            {
                if (tempv[i] == '=')
                {
                    Array.Resize(ref tempArr, tempArr.Length + 1);
                    tempArr[index] = tempv[i];
                    index++;
                    i++;
                    Array.Resize(ref tempArr, tempArr.Length + 1);
                    tempArr[index] = REPLACEMENTCHARACTER;
                    index++;
                    int found = 0;
                    int k = 0;
                    for (k = i; ((k < tempv.Length) && (int)tempv[k] != 32); k++)
                    {
                        if ((tempv[k] == '>' || tempv[k] == '/') && found == 0)
                        {
                            Array.Resize(ref tempArr, tempArr.Length + 1);
                            tempArr[index] = REPLACEMENTCHARACTER;
                            index++;
                            found = k;

                        }
                        Array.Resize(ref tempArr, tempArr.Length + 1);
                        tempArr[index] = tempv[k];
                        index++;
                        i++;
                    }
                    //Check for attributes (if more than one attributes are present)
                    if(found==0 && (int)(tempv[k])==32)
                     {
                        Array.Resize(ref tempArr, tempArr.Length + 1);
                        tempArr[index] = REPLACEMENTCHARACTER;
                        index++;
                    }

                    //Append replacement character it is not a space or end of tag.
                    if (((int)tempv[found] != 32 && tempv[found] != '>' && tempv[found] != '/') && found != 0 && tempv[found] != '"')
                    {
                        Array.Resize(ref tempArr, tempArr.Length + 1);
                        tempArr[index] = REPLACEMENTCHARACTER;
                        index++;
                    }

                    //Add any existing space as it is
                    if ((k < tempv.Length) && (int)tempv[k] == 32)
                    {
                        Array.Resize(ref tempArr, tempArr.Length + 1);
                        tempArr[index] = tempv[k];
                        index++;
                    }

                }
                else
                {
                    Array.Resize(ref tempArr, tempArr.Length + 1);
                    tempArr[index] = tempv[i];
                    index++;
                }

            }
            //convert character array to string
            string charToString = new string(tempArr);

            //Replace all replacement characters (added above) by the '\"'
            retValue = charToString.Replace(REPLACEMENTCHARACTER.ToString(), "\"");
            //Remove all escape charaters    
            retValue = retValue.Replace(@"\", string.Empty);

            retValue = retValue.Replace("\"", "'");

            return retValue;
        }
    }
}