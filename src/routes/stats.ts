import express from "express";
import { StatsController } from "../controllers/StatsController";

const router = express.Router();
const statsController = new StatsController();

// Route pour obtenir toutes les statistiques du tableau de bord
router.get("/dashboard", statsController.getDashboardStats);

// Route pour obtenir les statistiques quotidiennes
router.get("/daily", statsController.getDailyStats);

// Route pour obtenir les statistiques par type
router.get("/types", statsController.getTypeStats);

// Route pour obtenir les statistiques géographiques
router.get("/geographic", statsController.getGeographicStats);

export default router;
