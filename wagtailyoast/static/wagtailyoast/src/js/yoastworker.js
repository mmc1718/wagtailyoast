import { AnalysisWebWorker } from 'yoastseo';
import EnglishResearcher from 'yoastseo/build/languageProcessing/languages/en/Researcher';

// Run Yoast Worker

// TODO: choose language dynamically
const worker = new AnalysisWebWorker(self, new EnglishResearcher());
worker.register();
