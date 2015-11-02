using System;
using System.Linq;


namespace SpaceshipTracker.Web.Persistance
{
    public class SamplePositions
    {
        private SpaceshipTrackerContext _ctx;

        public SamplePositions(SpaceshipTrackerContext ctx)
        {
            _ctx = ctx;
        }

        public void InitializeData()
        {
            CreateVisits();
        }

        private void CreateVisits()
        {
            if (!_ctx.Positions.Any())
            {
                _ctx.Positions.Add(new Models.Position()
                {
                    Id = 0,
                    Longitude = 57.1,
                    Latitude = 11.2,
                    Timestamp = DateTime.Now,
                    Elevation= 32,
                    Identifier = "MyShip"
                });

                _ctx.Positions.Add(new Models.Position()
                {
                    Id = 0,
                    Longitude = 57.2,
                    Latitude = 11.3,
                    Timestamp = DateTime.Now.AddSeconds(1),
                    Elevation = 35,
                    Identifier = "MyShip"
                });
                _ctx.Positions.Add(new Models.Position()
                {
                    Id = 0,
                    Longitude = 57.4,
                    Latitude = 11.5,
                    Timestamp = DateTime.Now.AddSeconds(2),
                    Elevation = 38,
                    Identifier = "MyShip"
                });


                _ctx.SaveChanges();

            }
        }

    }
}