using IHSEnergy.Enerdeq.Session;

namespace IHS.EnergyWebServices.ExportFromQuerySample.Export.ExportStrategy
{
    /// <summary>
    /// Provides strategy to export data.
    /// </summary>
    public interface IExportStrategy
    {
        /// <summary>
        /// Exports data.
        /// </summary>
        /// <param name="options">Export parameters</param>
        void Export(WebServicesSession session, Options options);
    }
}
