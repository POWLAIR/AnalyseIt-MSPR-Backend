export interface DashboardStats {
  global_stats: {
    total_epidemics: number;
    active_epidemics: number;
    total_cases: number;
    total_deaths: number;
    mortality_rate: number;
  };
  type_distribution: Array<{
    type: string;
    epidemic_count: number;
    cases: number;
    deaths: number;
  }>;
  geographic_distribution: Array<{
    country: string;
    cases: number;
    deaths: number;
  }>;
  daily_evolution: Array<{
    date: string;
    new_cases: number;
    new_deaths: number;
    active_cases: number;
  }>;
  top_active_epidemics: Array<{
    id: number;
    name: string;
    type: string;
    country: string;
    total_cases: number;
    total_deaths: number;
  }>;
}

export interface DailyStats {
  id: number;
  date: string;
  cases: number;
  active: number;
  deaths: number;
  recovered: number;
  new_cases: number;
  new_deaths: number;
  new_recovered: number;
  epidemic: {
    id: number;
    name: string;
    type: string;
  };
  location: {
    country: string;
    region: string | null;
  };
}

export interface TypeDistribution {
  type: string;
  count: number;
  total_cases: number;
  total_deaths: number;
  avg_active_cases: number;
}

export interface GeographicDistribution {
  country: string;
  region: string | null;
  epidemic_count: number;
  total_cases: number;
  total_deaths: number;
  avg_active_cases: number;
}
