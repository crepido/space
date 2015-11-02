using Microsoft.AspNet.Builder;
using Microsoft.AspNet.Diagnostics.Entity;
using Microsoft.Framework.DependencyInjection;
using Microsoft.Framework.Logging;
using SpaceshipTracker.Web.Persistance;
using SpaceshipTracker.Web.Repositories;

namespace SpaceshipTracker.Web
{
    public class Startup
    {
        // For more information on how to configure your application, visit http://go.microsoft.com/fwlink/?LinkID=398940
        public void ConfigureServices(IServiceCollection services)
        {
            services.AddMvc();

            services.AddEntityFramework()
                .AddNpgsql()
                .AddDbContext<SpaceshipTrackerContext>();

            services.AddTransient<SamplePositions>();

            services.AddScoped<IPositionRepository, PositionRepository>();
            
        }

        public void Configure(
            IApplicationBuilder app,
            SamplePositions sampleDataInitializer,
            ILoggerFactory loggerfactory)
        {
            loggerfactory.AddConsole(minLevel: LogLevel.Verbose);

            app.UseDeveloperExceptionPage();

            app.UseMvc();

            sampleDataInitializer.InitializeData();
        }
    }
}
