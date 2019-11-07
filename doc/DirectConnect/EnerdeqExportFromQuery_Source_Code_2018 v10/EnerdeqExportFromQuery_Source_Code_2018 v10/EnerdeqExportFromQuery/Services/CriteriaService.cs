using IHS.EnergyWebServices.ExportFromQuerySample.Resources;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Xml.Linq;
using System.Xml.XPath;

namespace IHS.EnergyWebServices.ExportFromQuerySample.Services
{
    /// <summary>
    /// Utility class to handle CriteriaXml
    /// </summary>
    public static class CriteriaService
    {
        /// <summary>
        /// Creates XDocument from query string.
        /// </summary>
        /// <param name="query">query string</param>
        /// <returns>Query</returns>
        public static XDocument CreateQueryObject(string query)
        {
            if (string.IsNullOrWhiteSpace(query)) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            try
            {
                return XDocument.Parse(query);
            }
            catch
            {
                throw new ArgumentException("Query is in invalid format.");
            }
        }

        /// <summary>
        /// Gets first criteria in query that matches search parameters.
        /// </summary>
        /// <param name="query">Query</param>
        /// <param name="search">Search parameters</param>
        /// <returns>Criteria</returns>
        public static XElement GetCriteria(XDocument query, CriteriaSearch search)
        {
            if (query == null || search == null) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            return GetAllCriteria(query).Where(c => CriteriaMatch(c, search)).FirstOrDefault();
        }

        /// <summary>
        /// Gets all criteria from query.
        /// </summary>
        /// <param name="query">Query</param>
        /// <returns>Criteria</returns>
        public static IEnumerable<XElement> GetAllCriteria(XDocument query)
        {
            if (query == null) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            return query.XPathSelectElements("/criterias/criteria");
        }

        /// <summary>
        /// Gets all criteria from query that match search parameters.
        /// </summary>
        /// <param name="query">Query</param>
        /// <param name="search"></param>
        /// <returns>Criteria</returns>
        public static IEnumerable<XElement> GetAllCriteria(XDocument query, CriteriaSearch search)
        {
            if (query == null || search == null) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            return GetAllCriteria(query).Where(c => CriteriaMatch(c, search));
        }

        /// <summary>
        /// Adds criteria to query.
        /// </summary>
        /// <param name="query">Query</param>
        /// <param name="criteria">Criteria</param>
        public static void AddCriteria(XDocument query, XElement criteria)
        {
            if (query == null || criteria == null) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            GetAllCriteria(query).Last().AddAfterSelf(criteria);
        }

        /// <summary>
        /// Replaces first criteria from query that matches search parameters with replacement criteria.
        /// </summary>
        /// <param name="query">Query</param>
        /// <param name="search">Search parameters</param>
        /// <param name="criteria">Replacemente criteria</param>
        public static void ReplaceCriteria(XDocument query, CriteriaSearch search, XElement criteria)
        {
            if (query == null || search == null || criteria == null) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            GetAllCriteria(query, search).FirstOrDefault().ReplaceWith(criteria);
        }

        /// <summary>
        /// Creates Last Update Date criteria
        /// </summary>
        /// <param name="valueId">Filter value id</param>
        /// <param name="datatype">Datatype</param>
        /// <param name="attribute">Attribute name</param>
        /// <param name="filterLogic">Filter logic</param>
        /// <param name="startDate">Last update date</param>
        /// <returns>Last Update Date criteria</returns>
        public static XElement CreateLastUpdateCriteria(string valueId, string datatype, string attribute, string filterLogic, DateTime startDate, string Domain)
        {
               return BuildLastUpdateCriteria(valueId, datatype, attribute, filterLogic, CreateActualDateValue(startDate, filterLogic), CreateDisplayDateValue(startDate, filterLogic), Domain);

           }

        /// <summary>
        /// Creates Last Update Date criteria
        /// </summary>
        /// <param name="valueId">Filter value id</param>
        /// <param name="datatype">Datatype</param>
        /// <param name="attribute">Attribute name</param>
        /// <param name="startDate">Last update start date</param>
        /// <param name="endDate">Last update end date</param>
        /// <returns>Last Update Date criteria</returns>
        public static XElement CreateLastUpdateCriteria(string valueId, string datatype, string attribute, DateTime startDate, DateTime endDate, string Domain)
        {
            return BuildLastUpdateCriteria(valueId, datatype, attribute, FilterLogic.Between, CreateBetweenActualDateValue(startDate, endDate), CreateBetweenDisplayDateValue(startDate, endDate), Domain);
        }

        /// <summary>
        /// Gets the datatype from criteria.
        /// </summary>
        /// <param name="criteria">Criteria</param>
        /// <returns>Datatype</returns>
        public static string GetCriteriaDataType(XElement criteria)
        {
            if (criteria == null) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            try
            {
                return criteria.Element("datatype").FirstNode.ToString();
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Gets the domain from criteria.
        /// </summary>
        /// <param name="criteria">Criteria</param>
        /// <returns>Domain</returns>
        public static string GetCriteriaDomain(XElement criteria)
        {
            if (criteria == null) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            try
            {
                return criteria.Element("domain").FirstNode.ToString();
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Gets the attribute group from criteria.
        /// </summary>
        /// <param name="criteria">Criteria</param>
        /// <returns>Attribute group</returns>
        public static string GetCriteriaAttributeGroup(XElement criteria)
        {
            if (criteria == null) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            try
            {
                return criteria.Element("attribute_group").FirstNode.ToString();
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Gets the attribute from criteria.
        /// </summary>
        /// <param name="criteria">Criteria</param>
        /// <returns>Attribute</returns>
        public static string GetCriteriaAttribute(XElement criteria)
        {
            if (criteria == null) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            try
            {
                return criteria.Element("attribute").FirstNode.ToString();
            }
            catch
            {
                return null;
            }
        }

        /// <summary>
        /// Creates Last Update Date criteria
        /// </summary>
        /// <param name="valueId">Filter value id</param>
        /// <param name="datatype">Datatype</param>
        /// <param name="attribute">Attribute name</param>
        /// <param name="filterLogic">Filter logic</param>
        /// <param name="actual">Filter actual value</param>
        /// <param name="display">Filter display value</param>
        /// <returns>Last Update Date criteria</returns>
        private static XElement BuildLastUpdateCriteria(string valueId, string datatype, string attribute, string filterLogic, string actual, string display, string domain)
        {
            if (string.IsNullOrWhiteSpace(valueId) ||
                string.IsNullOrWhiteSpace(datatype) ||
                string.IsNullOrWhiteSpace(attribute) ||
                string.IsNullOrWhiteSpace(filterLogic) ||
                string.IsNullOrWhiteSpace(actual) ||
                string.IsNullOrWhiteSpace(display)) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);

            var criteria = new XElement("criteria", new XAttribute("type", "value"),
                new XAttribute("ignored", "false"));

            criteria.Add(new XElement("domain", domain),
                new XElement("datatype", datatype),
                new XElement("attribute_group", "Date"),
                new XElement("attribute", attribute),
                new XElement("type", "date"));

            var filter = new XElement("filter", new XAttribute("logic", filterLogic));

            filter.Add(new XElement("value", new XAttribute("id", valueId),
                new XAttribute("actual", actual),
                new XAttribute("display", display),
                new XAttribute("ignored", "false")));

            criteria.Add(filter);
            return criteria;
        }

        /// <summary>
        /// Creates Last Update Date display value.
        /// </summary>
        /// <param name="startDate">Last update start date</param>
        /// <param name="logic">Filter logic</param>
        /// <returns>Last Update Date display value</returns>
        private static string CreateDisplayDateValue(DateTime startDate, string logic)
        {
            if (startDate == null || string.IsNullOrWhiteSpace(logic)) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);

            var display = string.Empty;
            if (logic.Equals(FilterLogic.GreaterThanOrEquals, StringComparison.OrdinalIgnoreCase))
            {
                display += "after " + startDate.ToString("MM/dd/yyyy");
            }
            else if (logic.Equals(FilterLogic.LessThanOrEquals, StringComparison.OrdinalIgnoreCase))
            {
                display += "before " + startDate.ToString("MM/dd/yyyy");
            }
            return display;
        }

        /// <summary>
        /// Creates Last Update Date display value.
        /// </summary>
        /// <param name="startDate">Last update start date</param>
        /// <param name="endDate">Last update end date</param>
        /// <returns>Last Update Date display value</returns>
        private static string CreateBetweenDisplayDateValue(DateTime startDate, DateTime endDate)
        {
            if (startDate == null || startDate == null) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            return "between " +
                startDate.ToString("MM/dd/yyyy") +
                " and " +
                endDate.ToString("MM/dd/yyyy");
        }

        /// <summary>
        /// Creates Last Update Date actual value.
        /// </summary>
        /// <param name="startDate">Last update start date</param>
        /// <param name="logic">Filter logic</param>
        /// <returns>Last update Date actual value</returns>
        private static string CreateActualDateValue(DateTime startDate, string logic)
        {
            if (startDate == null) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            if (string.IsNullOrWhiteSpace(logic)) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);

            var actual = string.Empty;
            if (logic.Equals(FilterLogic.GreaterThanOrEquals, StringComparison.OrdinalIgnoreCase))
            {
                actual += startDate.ToString("yyyy/MM/dd") + " 00:00:00";
            }
            else if (logic.Equals(FilterLogic.LessThanOrEquals, StringComparison.OrdinalIgnoreCase))
            {
                actual += startDate.ToString("yyyy/MM/dd") + " 23:59:59.999999999";
            }
            return actual;
        }

        /// <summary>
        /// Creates Last Update Date actual value.
        /// </summary>
        /// <param name="startDate">>Last update start date</param>
        /// <param name="endDate">>Last update end date</param>
        /// <returns>Last update Date actual value</returns>
        private static string CreateBetweenActualDateValue(DateTime startDate, DateTime endDate)
        {
            if (startDate == null || startDate == null) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            return startDate.ToString("yyyy/MM/dd") +
                " 00:00:00--" +
                endDate.ToString("yyyy/MM/dd") +
                " 23:59:59.999999999";
        }

        /// <summary>
        /// Checks if criteria matches search parameters.
        /// </summary>
        /// <param name="criteria">Criteria</param>
        /// <param name="search">Search parameters</param>
        /// <returns>True or false</returns>
        private static bool CriteriaMatch(XElement criteria, CriteriaSearch search)
        {
            if (criteria == null || search == null) throw new ArgumentException(Messages.ErrorMessages.RequestFailed);
            try
            {
                if (!string.IsNullOrWhiteSpace(search.Domain) &&
                    !GetCriteriaDomain(criteria).Equals(search.Domain, StringComparison.OrdinalIgnoreCase)) return false;
                if (!string.IsNullOrWhiteSpace(search.Datatype) &&
                    !GetCriteriaDataType(criteria).Equals(search.Datatype, StringComparison.OrdinalIgnoreCase)) return false;
                if (!string.IsNullOrWhiteSpace(search.AttributeGroup) &&
                    !GetCriteriaAttributeGroup(criteria).Equals(search.AttributeGroup, StringComparison.OrdinalIgnoreCase)) return false;
                if (!string.IsNullOrWhiteSpace(search.Attribute) &&
                    !GetCriteriaAttribute(criteria).Equals(search.Attribute, StringComparison.OrdinalIgnoreCase)) return false;
                return true;
            }
            catch
            {
                return false;
            }
        }

        /// <summary>
        /// Contains Filter logic options.
        /// </summary>
        public static class FilterLogic
        {
            public const string GreaterThanOrEquals = "greater_than_or_equals";
            public const string LessThanOrEquals = "less_than_or_equals";
            public const string Between = "between";
        }

        /// <summary>
        /// Search object used to search for criteria in queries.
        /// </summary>
        public class CriteriaSearch
        {
            public string Domain { get; set; }
            public string Datatype { get; set; }
            public string Attribute { get; set; }
            public string AttributeGroup { get; set; }
        }
    }
}