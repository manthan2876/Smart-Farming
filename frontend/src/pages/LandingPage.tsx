import { Link } from "react-router-dom";
import { Sprout, Droplet, Bug } from "lucide-react";
import { motion } from "motion/react";
import PublicNav from "../components/PublicNav";

export default function LandingPage() {
  return (
    <div className="min-h-screen overflow-hidden bg-canvas">
      <PublicNav />

      {/* Hero Section */}
      <section className="mx-auto grid max-w-7xl gap-8 px-5 pb-12 pt-8 sm:px-8 lg:grid-cols-[1.05fr_0.95fr] lg:gap-12 lg:pb-20 lg:pt-16">
        <div className="flex min-h-[32rem] flex-col justify-between rounded-lg bg-farmer-100 p-7 sm:p-10 lg:p-14">
          <motion.h1
            className="max-w-xl font-display text-display text-ink"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            Smarter Farming Starts Here
          </motion.h1>
          
          <motion.div
            className="flex flex-1 items-center justify-center py-10"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <Sprout className="h-20 w-20 text-farmer-700" strokeWidth={1} />
          </motion.div>

          <div className="space-y-6">
            <p className="max-w-md text-base leading-7 text-muted">
              <strong className="text-ink">[We are Marbam,]</strong><br/>
              We turn your farm's data into clear, simple actions that boost efficiency, increase yield, and improve your bottom line.
            </p>
            <div className="flex flex-wrap gap-3">
              <Link to="/auth/register" className="rounded-sm bg-farmer-700 px-5 py-3 text-sm font-bold text-white shadow-soft transition-colors hover:bg-farmer-800">Start A Demo</Link>
              <Link to="/services" className="rounded-sm border border-farmer-700 px-5 py-3 text-sm font-bold text-farmer-800 transition-colors hover:bg-farmer-200">Learn More</Link>
            </div>
          </div>
        </div>

        <div className="relative min-h-[32rem] overflow-hidden rounded-lg bg-ink">
          <img className="absolute inset-0 h-full w-full object-cover opacity-90" src="https://images.unsplash.com/photo-1625246333195-78d9c38ad449?q=80&w=2070&auto=format&fit=crop" alt="Farmer in field" />
          <div className="absolute inset-x-0 bottom-0 grid gap-3 bg-ink/85 p-6 text-white backdrop-blur-sm sm:grid-cols-2">
            <div>
              <h4 className="font-display text-lg"><span className="mr-2 text-farmer-300">[01]</span>32% Higher Yields</h4>
              <p className="mt-1 text-sm text-white/70">From every treated acre</p>
            </div>
            <div>
              <h4 className="font-display text-lg"><span className="mr-2 text-farmer-300">[02]</span>45% Less Water Use</h4>
              <p className="mt-1 text-sm text-white/70">Per ton of crop</p>
            </div>
          </div>
        </div>
      </section>

      {/* Impact Section */}
      <section className="mx-auto grid max-w-7xl gap-8 px-5 py-16 sm:px-8 lg:grid-cols-[0.35fr_0.65fr] lg:py-24">
        <div className="font-display text-2xl text-farmer-700">
          The Impact of Smarter Decisions
        </div>
        <div>
          <h2 className="max-w-3xl font-display text-xl leading-8 text-ink sm:text-2xl">When intelligence guides your operation, the results speak for themselves. From row crops to orchards and greenhouse, our clients achieve:</h2>
          
          <div className="mt-10 grid gap-5 sm:grid-cols-2">
            <div className="rounded-md border border-line bg-surface p-6 shadow-soft">
              <h4 className="font-display text-3xl text-farmer-700"><span className="mr-2 text-sm text-muted">[01]</span>40%</h4>
              <p className="mt-2 text-sm text-muted">More Efficient Water &<br/>Nutrient Use</p>
            </div>
            <div className="rounded-md border border-line bg-surface p-6 shadow-soft">
              <Droplet className="text-expert-500" size={32} />
              <h4 className="mt-4 font-display text-3xl text-farmer-700"><span className="mr-2 text-sm text-muted">[02]</span>Up to 25%</h4>
              <p className="mt-2 text-sm text-muted">Higher Harvest Value</p>
            </div>
            <div className="rounded-md border border-line bg-surface p-6 shadow-soft">
              <h4 className="font-display text-3xl text-farmer-700"><span className="mr-2 text-sm text-muted">[03]</span>98%</h4>
              <p className="mt-2 text-sm text-muted">Accuracy in Predictive<br/>Threat Detection</p>
            </div>
            <div className="rounded-md border border-line bg-surface p-6 shadow-soft">
              <Bug className="text-admin-500" size={32} />
              <h4 className="mt-4 font-display text-3xl text-farmer-700"><span className="mr-2 text-sm text-muted">[04]</span>Millions</h4>
              <p className="mt-2 text-sm text-muted">of smart decisions made<br/>daily across our network</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
