using System.Collections.Generic;
using SpaceshipTracker.Web.Models;

namespace SpaceshipTracker.Web.Repositories
{
    public interface IPositionRepository
    {
        IList<Position> GetAll();
        IEnumerable<Position> GetAllByIdentifier(string identifier);
        void Save(Position position);
        IEnumerable<string> GetAllShipNames();
    }
}