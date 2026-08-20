import { AnalysisWebWorker } from 'yoastseo';
import EnglishResearcher from "yoastseo/build/languageProcessing/languages/en/Researcher";
import GermanResearcher from "yoastseo/build/languageProcessing/languages/de/Researcher";


const pageLocale = new URL(self.location.href).searchParams.get('locale');

let langResearcher;
if (pageLocale == 'de') {
    langResearcher = new GermanResearcher();
} else {
    langResearcher = new EnglishResearcher();
}

// Run Yoast Worker

const worker = new AnalysisWebWorker(self, langResearcher);
worker.register();
