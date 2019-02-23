    using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using IHSEnergy.Enerdeq.Session;
using IHSEnergy.Enerdeq.ExportBuilder;
using System.IO;
using EnerdeqExportFromQuery.Utility;

namespace IHS.EnergyWebServices.ExportFromQuerySample.Export.ExportStrategy
{
    public class SpatialExportStrategy : IExportStrategy
    {
        private static readonly TaskFactory _taskFactory = new TaskFactory();

        public void Export(WebServicesSession session, Options options)
        {
            try
            {
                using (ExportBuilder _exportBuilder = new ExportBuilder(session))
                {

                    IList<string> layers = options.SpatialExports;
                    // var fileName = string.Format("SpatialExport{0}", Guid.NewGuid());
                    var fileName = "SpatialExport-";
                    
                    string[] latLong = parseLatLong(options.SpatialExtent);
                    string[] tileSizes = parseTileSize(options.SpatialTileSize);

                    var tileRow = Double.Parse(tileSizes[0]);
                    var tileCol = Double.Parse(tileSizes[1]);
                    var minLat = GetDouble(latLong[0], -90);
                    var maxLat = GetDouble(latLong[1], 90);
                    var minLong = GetDouble(latLong[2], -180);
                    var maxLong = GetDouble(latLong[3], 180);
                    var newMaxLat = maxLat;
                    var newMaxLong = maxLong;

                    var tasks = new List<Task>();

                    for (double row= minLat;row<=maxLat;row+=tileRow)
                    {
                        for(double col = minLong;col<maxLong; col+=tileCol)
                        {
                            newMaxLat = maxLat > (row + tileRow) ? (row + tileRow) : maxLat;
                            newMaxLong = maxLong > (col + tileCol) ? (col + tileCol) : maxLong;
                            fileName = "SpatialExport-";
                            fileName = generateFileName(fileName, newMaxLat, newMaxLong, row, col);

                            string jobId = _exportBuilder.BuildSpatial(row, newMaxLat,
                                    col, newMaxLong, layers.ToArray(), fileName,
                                     (options.SpatialExportOverWrite.HasValue && options.SpatialExportOverWrite.Value), 
                                     options.SpatialFormat);
                            

                            Console.WriteLine("\nSpatial Export File created  : " + jobId);

                            Console.WriteLine("\nRetrieving the Spatial Export Status for  : " + jobId);

                            Console.WriteLine("\nPlease Wait...");

                            //  Store file in temp directory
                            var tempFilename = Path.Combine(options.WorkingDirectory, jobId);

                            var task = _taskFactory.StartNew(() =>
                            
                            EwsUtility.RetrieveFile(_exportBuilder, jobId, tempFilename, options.Verbose));

                            if (options.Verbose) Console.Out.WriteLine("File '{0}' created. ", tempFilename);

                            Console.WriteLine("\nSpatial Export Completed Successfully  : " + jobId
                            );
                            tasks.Add(task);
                        }
                    }
                    Task.WaitAll(tasks.ToArray());

                    Console.WriteLine("\nAll Spatial Export Completed Successfully");

                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("\nSpatial Export Error : " + ex.Message.ToString());
                     
            }
 }


        private static string generateFileName(string fileName, double tileRow, double tileCol, double row, double col)
        {
            fileName = fileName + row + "-" + tileRow + "_" + col + "-" + tileCol;
            return fileName;
        }

        private string[] parseTileSize(string tileSize)
        {
            Char delimiter = 'X';
            return tileSize.Split(delimiter);
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="extent"></param>
        /// <returns></returns>
        private string[] parseLatLong(string extent)
        {

            string[] latLongSubstrings;
            extent = extent.Replace(")(", ",");
            extent = extent.Replace('(', ' ');
            extent = extent.Replace(')', ' ');
            Char delimiter = ',';
            latLongSubstrings = extent.Split(delimiter);
            return latLongSubstrings;
        }
        
        /// <summary>
        /// 
        /// </summary>
        /// <param name="text"></param>
        /// <param name="defaultValue"></param>
        /// <returns></returns>
        private double GetDouble(string text, double defaultValue)
        {
            double outValue;
            return Double.TryParse(text, out outValue) ? outValue : defaultValue;
        }

    }
}
