import homePage from './homePage'
import Navbar from './Navbar'
import summariesAndNotes from './summariesAndNotes'
import mislandIndicators from './mislandIndicators'
import mainIndicators from './Dashboard/Indicators'
import subIndicators from './Dashboard/SubIndicators'
export default {

  logo: {
    title: "MISLAND",
  },
 ...homePage,
 ...Navbar,
 ...summariesAndNotes,
 ...mislandIndicators,
 ...mainIndicators,
 ...subIndicators,
}
