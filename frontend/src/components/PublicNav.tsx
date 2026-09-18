import { Link } from "react-router-dom";

export default function PublicNav() {
  return (
    <nav className="mx-auto flex w-full max-w-7xl flex-wrap items-center justify-between gap-4 px-5 py-5 sm:px-8">
      <Link to="/" className="flex items-center gap-3 text-ink">
        <span className="flex h-10 w-10 items-center justify-center rounded-md bg-farmer-700 text-sm font-bold text-white">SF</span>
        <span className="font-display text-xl">Smart Farming</span>
      </Link>
      <div className="flex flex-wrap items-center justify-end gap-x-5 gap-y-2 text-sm font-semibold text-muted">
        <Link className="transition-colors hover:text-farmer-700" to="/">Home</Link>
        <Link className="transition-colors hover:text-farmer-700" to="/about">About</Link>
        <Link className="transition-colors hover:text-farmer-700" to="/services">Services</Link>
        <Link className="transition-colors hover:text-farmer-700" to="/crops">Supported Crops</Link>
        <Link className="rounded-sm bg-farmer-700 px-4 py-2.5 text-white shadow-soft transition-colors hover:bg-farmer-800" to="/auth/login">Sign In</Link>
      </div>
    </nav>
  );
}
