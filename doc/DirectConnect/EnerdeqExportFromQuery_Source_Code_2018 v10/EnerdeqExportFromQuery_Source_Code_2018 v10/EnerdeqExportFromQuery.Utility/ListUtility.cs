using System.Collections.Generic;
using System.Linq;

namespace EnerdeqExportFromQuery.Utility
{
    /// <summary>
    /// Provides a collection of helper functions to use with Lists.
    /// </summary>
    public static class ListUtility
    {
        /// <summary>
        /// Splits an Enumerable collection into multiple Enumerable collections of elements.
        /// </summary>
        /// <typeparam name="T">Type of Enumerable collection.</typeparam>
        /// <param name="list">Enumerable collection of elements.</param>
        /// <param name="chunkSize">Max size of resulting Enumerable collections.</param>
        /// <returns></returns>
        public static IEnumerable<IEnumerable<T>> Chunk<T>(this IEnumerable<T> list, int chunkSize)
        {
            var i = 0;
            var chunks = from name in list
                         group name by i++ / chunkSize into part
                         select part.AsEnumerable<T>();
            return chunks;
        }

        /// <summary>
        /// Checks if Enumerable collection is null or empty.
        /// </summary>
        /// <typeparam name="T">Type of Enumerable collection.</typeparam>
        /// <param name="list">Enumerable collection of elements.</param>
        /// <returns>true or false</returns>
        public static bool IsNullorEmpty<T>(this IEnumerable<T> list)
        {
            return list == null || !list.Any();
        }
    }
}