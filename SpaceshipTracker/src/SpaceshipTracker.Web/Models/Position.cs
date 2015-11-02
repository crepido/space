using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace SpaceshipTracker.Web.Models
{
    public class Position
    {
        public double Longitude { get; set; }
        public double Latitude { get; set; }
        public double Elevation { get; set; }
        public string Identifier { get; set; }
        public DateTime Timestamp { get; set; }
        public int Id { get; set; }
    }
}
