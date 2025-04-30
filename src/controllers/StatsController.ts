import { Request, Response } from "express";
import { StatsService } from "../services/StatsService";

const statsService = new StatsService();

export class StatsController {
  async getDashboardStats(req: Request, res: Response) {
    try {
      const stats = await statsService.getDashboardStats();
      res.json(stats);
    } catch (error) {
      console.error("Error fetching dashboard stats:", error);
      res.status(500).json({
        error: "Erreur lors de la récupération des statistiques",
      });
    }
  }

  async getDailyStats(req: Request, res: Response) {
    try {
      const epidemicId = req.query.epidemicId
        ? parseInt(req.query.epidemicId as string)
        : undefined;

      const stats = await statsService.getDailyStats(epidemicId);
      res.json(stats);
    } catch (error) {
      console.error("Error fetching daily stats:", error);
      res.status(500).json({
        error: "Erreur lors de la récupération des statistiques quotidiennes",
      });
    }
  }

  async getTypeStats(req: Request, res: Response) {
    try {
      const stats = await statsService.getTypeStats();
      res.json(stats);
    } catch (error) {
      console.error("Error fetching type stats:", error);
      res.status(500).json({
        error: "Erreur lors de la récupération des statistiques par type",
      });
    }
  }

  async getGeographicStats(req: Request, res: Response) {
    try {
      const stats = await statsService.getGeographicStats();
      res.json(stats);
    } catch (error) {
      console.error("Error fetching geographic stats:", error);
      res.status(500).json({
        error: "Erreur lors de la récupération des statistiques géographiques",
      });
    }
  }
}
