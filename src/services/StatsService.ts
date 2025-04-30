import { db } from "../config/database";
import {
  DashboardStats,
  DailyStats,
  TypeDistribution,
  GeographicDistribution,
} from "../types/stats";

export class StatsService {
  async getDashboardStats(): Promise<DashboardStats> {
    // Statistiques globales
    const globalStats = await db.query(`
            SELECT 
                COUNT(DISTINCT e.id) as total_epidemics,
                COUNT(DISTINCT CASE WHEN e.end_date IS NULL THEN e.id END) as active_epidemics,
                SUM(ds.cases) as total_cases,
                SUM(ds.deaths) as total_deaths,
                ROUND(CAST(SUM(ds.deaths) AS FLOAT) / NULLIF(SUM(ds.cases), 0) * 100, 2) as mortality_rate
            FROM Epidemic e
            LEFT JOIN Daily_stats ds ON e.id = ds.id_epidemic
            WHERE ds.date = (
                SELECT MAX(date) 
                FROM Daily_stats 
                WHERE id_epidemic = e.id
            )
        `);

    // Distribution par type
    const typeDistribution = await db.query(`
            SELECT 
                e.type,
                COUNT(DISTINCT e.id) as epidemic_count,
                SUM(ds.cases) as cases,
                SUM(ds.deaths) as deaths
            FROM Epidemic e
            LEFT JOIN Daily_stats ds ON e.id = ds.id_epidemic
            WHERE ds.date = (
                SELECT MAX(date) 
                FROM Daily_stats 
                WHERE id_epidemic = e.id
            )
            GROUP BY e.type
            ORDER BY cases DESC
        `);

    // Distribution géographique
    const geographicDistribution = await db.query(`
            SELECT 
                l.country,
                SUM(ds.cases) as cases,
                SUM(ds.deaths) as deaths
            FROM Daily_stats ds
            JOIN Localisation l ON ds.id_loc = l.id
            WHERE ds.date = (
                SELECT MAX(date) 
                FROM Daily_stats 
                WHERE id_epidemic = ds.id_epidemic
            )
            GROUP BY l.country
            ORDER BY cases DESC
            LIMIT 10
        `);

    // Évolution quotidienne (30 derniers jours)
    const dailyEvolution = await db.query(`
            SELECT 
                ds.date,
                SUM(ds.new_cases) as new_cases,
                SUM(ds.new_deaths) as new_deaths,
                SUM(ds.active) as active_cases
            FROM Daily_stats ds
            WHERE ds.date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY ds.date
            ORDER BY ds.date
        `);

    // Top épidémies actives
    const topActiveEpidemics = await db.query(`
            SELECT 
                e.id,
                e.name,
                e.type,
                l.country,
                ds.cases as total_cases,
                ds.deaths as total_deaths
            FROM Epidemic e
            JOIN Daily_stats ds ON e.id = ds.id_epidemic
            JOIN Localisation l ON ds.id_loc = l.id
            WHERE e.end_date IS NULL
            AND ds.date = (
                SELECT MAX(date) 
                FROM Daily_stats 
                WHERE id_epidemic = e.id
            )
            ORDER BY ds.cases DESC
            LIMIT 5
        `);

    return {
      global_stats: {
        total_epidemics: globalStats[0].total_epidemics,
        active_epidemics: globalStats[0].active_epidemics,
        total_cases: globalStats[0].total_cases,
        total_deaths: globalStats[0].total_deaths,
        mortality_rate: globalStats[0].mortality_rate,
      },
      type_distribution: typeDistribution.map((type) => ({
        type: type.type,
        epidemic_count: type.epidemic_count,
        cases: type.cases,
        deaths: type.deaths,
      })),
      geographic_distribution: geographicDistribution.map((geo) => ({
        country: geo.country,
        cases: geo.cases,
        deaths: geo.deaths,
      })),
      daily_evolution: dailyEvolution.map((day) => ({
        date: day.date,
        new_cases: day.new_cases,
        new_deaths: day.new_deaths,
        active_cases: day.active_cases,
      })),
      top_active_epidemics: topActiveEpidemics.map((epidemic) => ({
        id: epidemic.id,
        name: epidemic.name,
        type: epidemic.type,
        country: epidemic.country,
        total_cases: epidemic.total_cases,
        total_deaths: epidemic.total_deaths,
      })),
    };
  }

  async getDailyStats(epidemicId?: number): Promise<DailyStats[]> {
    const query = `
            SELECT 
                ds.id,
                ds.date,
                ds.cases,
                ds.active,
                ds.deaths,
                ds.recovered,
                ds.new_cases,
                ds.new_deaths,
                ds.new_recovered,
                e.id as epidemic_id,
                e.name as epidemic_name,
                e.type as epidemic_type,
                l.country,
                l.region
            FROM Daily_stats ds
            JOIN Epidemic e ON ds.id_epidemic = e.id
            JOIN Localisation l ON ds.id_loc = l.id
            ${epidemicId ? "WHERE ds.id_epidemic = ?" : ""}
            ORDER BY ds.date DESC
            LIMIT 100
        `;

    const params = epidemicId ? [epidemicId] : [];
    const results = await db.query(query, params);

    return results.map((row) => ({
      id: row.id,
      date: row.date,
      cases: row.cases,
      active: row.active,
      deaths: row.deaths,
      recovered: row.recovered,
      new_cases: row.new_cases,
      new_deaths: row.new_deaths,
      new_recovered: row.new_recovered,
      epidemic: {
        id: row.epidemic_id,
        name: row.epidemic_name,
        type: row.epidemic_type,
      },
      location: {
        country: row.country,
        region: row.region,
      },
    }));
  }

  async getTypeStats(): Promise<TypeDistribution[]> {
    const results = await db.query(`
            SELECT 
                e.type,
                COUNT(DISTINCT e.id) as count,
                SUM(ds.cases) as total_cases,
                SUM(ds.deaths) as total_deaths,
                ROUND(AVG(ds.active), 0) as avg_active_cases
            FROM Epidemic e
            LEFT JOIN Daily_stats ds ON e.id = ds.id_epidemic
            WHERE ds.date = (
                SELECT MAX(date) 
                FROM Daily_stats 
                WHERE id_epidemic = e.id
            )
            GROUP BY e.type
            ORDER BY total_cases DESC
        `);

    return results.map((row) => ({
      type: row.type,
      count: row.count,
      total_cases: row.total_cases,
      total_deaths: row.total_deaths,
      avg_active_cases: row.avg_active_cases,
    }));
  }

  async getGeographicStats(): Promise<GeographicDistribution[]> {
    const results = await db.query(`
            SELECT 
                l.country,
                l.region,
                COUNT(DISTINCT e.id) as epidemic_count,
                SUM(ds.cases) as total_cases,
                SUM(ds.deaths) as total_deaths,
                ROUND(AVG(ds.active), 0) as avg_active_cases
            FROM Localisation l
            JOIN Daily_stats ds ON l.id = ds.id_loc
            JOIN Epidemic e ON ds.id_epidemic = e.id
            WHERE ds.date = (
                SELECT MAX(date) 
                FROM Daily_stats 
                WHERE id_epidemic = e.id
            )
            GROUP BY l.country, l.region
            ORDER BY total_cases DESC
        `);

    return results.map((row) => ({
      country: row.country,
      region: row.region || null,
      epidemic_count: row.epidemic_count,
      total_cases: row.total_cases,
      total_deaths: row.total_deaths,
      avg_active_cases: row.avg_active_cases,
    }));
  }
}
