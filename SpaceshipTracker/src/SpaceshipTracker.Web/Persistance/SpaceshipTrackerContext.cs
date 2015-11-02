using Microsoft.Data.Entity;
using Npgsql;
using SpaceshipTracker.Web.Models;

namespace SpaceshipTracker.Web.Persistance
{
    public class SpaceshipTrackerContext : DbContext
    {
        public DbSet<Position> Positions { get; set; }

        protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        {            
            optionsBuilder.UseNpgsql("Server=spaceshiptracker-dev-1.glenngbg.cont.tutum.io; " +
                    "User Id=postgres;Password=Crep123!;Database=spaceshiptracker-dev2;");
        }

        protected override void OnModelCreating(ModelBuilder modelBuilder)
        {

            modelBuilder.HasDefaultSchema("public");
            modelBuilder.Entity<Position>()
                .HasKey(p => p.Id);
        }
    }
}
