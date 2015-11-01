using SpaceshipTracker.Web.Models;
using SpaceshipTracker.Web.Persistance;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;

namespace SpaceshipTracker.Web.Repositories
{
    public class PositionRepository : IPositionRepository
    {
        private readonly SpaceshipTrackerContext _ctx;

        public PositionRepository(SpaceshipTrackerContext ctx)
        {
            _ctx = ctx;
        }
        public IList<Position> GetAll()
        {
            return _ctx.Positions.ToList();
        }

        public void Save(Position position)
        {
            _ctx.Positions.Add(position);
            _ctx.SaveChanges();
        }

        public IEnumerable<Position> GetAllByIdentifier(string identifier)
        {
            return _ctx.Positions.Where(p=>p.Identifier.Equals(identifier)).ToList();
        }
    }
}
