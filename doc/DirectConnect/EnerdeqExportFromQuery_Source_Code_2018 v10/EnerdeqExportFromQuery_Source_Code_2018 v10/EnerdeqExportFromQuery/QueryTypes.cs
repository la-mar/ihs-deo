using System.IO;

namespace IHS.EnergyWebServices.ExportFromQuerySample
{
    /// <summary>
    /// Gets data on the type of query.
    /// </summary>
    public static class QueryTypes
    {
        /// <summary>
        /// Query types
        /// </summary>
        public enum QueryType
        {
            QueryName,
            CriteriaXml,
            Ids
        }

        /// <summary>
        /// Returns the type of query.
        /// </summary>
        /// <param name="query">Query name or file name containing criteriaXml or list of Ids.</param>
        /// <returns>Querty type</returns>
        public static QueryType GetQueryType(string query)
        {
            if ((query.EndsWith(".qry") || query.EndsWith(".xml")) && query.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0 && File.Exists(query))
            {
                return QueryType.CriteriaXml;
            }
            else if (query.EndsWith(".txt") && query.IndexOfAny(Path.GetInvalidFileNameChars()) >= 0 && File.Exists(query))
            {
                return QueryType.Ids;
            }
            else
            {
                return QueryType.QueryName;
            }
        }
    }
}
