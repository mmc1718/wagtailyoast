import { AnalysisWebWorker } from 'yoastseo';
import EnglishResearcher from "yoastseo/build/languageProcessing/languages/en/Researcher";
import GermanResearcher from "yoastseo/build/languageProcessing/languages/de/Researcher";


const pageLocale = new URL(self.location.href).searchParams.get('locale');

const langResearcher = () => {
    if(pageLocale == 'en') {
    return new EnglishResearcher();
} else if (pageLocale == 'de') {
    return new GermanResearcher();
} console.log('unable to determine locale');
}


// Run Yoast Worker

const worker = new AnalysisWebWorker(self, langResearcher());
worker.register();
