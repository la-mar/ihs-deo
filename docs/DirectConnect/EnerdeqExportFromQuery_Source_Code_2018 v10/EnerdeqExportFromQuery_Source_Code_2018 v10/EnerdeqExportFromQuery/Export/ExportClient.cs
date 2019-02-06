using IHS.EnergyWebServices.ExportFromQuerySample.Export.ExportStrategy;
using IHSEnergy.Enerdeq.Session;
using System;

namespace IHS.EnergyWebServices.ExportFromQuerySample.Export
{
    /// <summary>
    /// Exports data from Enerdeq Web Services
    /// </summary>
    public class ExportClient
    {
        private WebServicesSession _session;
        private IExportStrategy _exportStrategy;

        /// <summary>
        /// Creates ExportClient object.
        /// </summary>
        /// <param name="session">Active Enerdeq Web Service session</param>
        public ExportClient(WebServicesSession session)
        {
            if (session == null) throw new ArgumentNullException("Session is invalid.");
            _session = session;
        }

        /// <summary>
        /// Creates ExportClient object.
        /// </summary>
        /// <param name="session">Active Enerdeq Web Service session</param>
        /// <param name="strategy">Exporting strategy</param>
        public ExportClient(WebServicesSession session, IExportStrategy strategy)
        {
            if(session == null) throw new ArgumentNullException("Session is invalid.");
            _session = session;
            _exportStrategy = strategy;
        }

        /// <summary>
        /// Sets export strategy
        /// </summary>
        /// <param name="strategy">Export strategy</param>
        public void SetExportStrategy(IExportStrategy strategy)
        {
            _exportStrategy = strategy;
        }

        /// <summary>
        /// Exports data using set export strategy.
        /// </summary>
        /// <param name="options">Export parameters</param>
        public void Export(Options options)
        {
            if (_exportStrategy == null) throw new ArgumentNullException("Export strategy is null.");
            _exportStrategy.Export(_session, options);
        }

        /// <summary>
        /// Exports data
        /// </summary>
        /// <param name="options">Export parameters</param>
        /// <param name="strategy">Export strategy</param>
        public void Export(Options options, IExportStrategy strategy)
        {
            strategy.Export(_session, options);
        }
    }
}
