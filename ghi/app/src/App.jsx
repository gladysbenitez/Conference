import { BrowserRouter, Route, Routes } from "react-router-dom";
import './App.css';
import AttendConferenceForm from './AttendConferenceForm';
import AttendeesList from './AttendeesList';
import ConferenceForm from './ConferenceForm';
import LocationForm from './LocationForm';
import MainPage from "./MainPage";
import Nav from './Nav';
import PresentationForm from "./PresentationForm";

function App(props) {

  return (
    <BrowserRouter>
      <Nav />
      <Routes>
        <Route index element={<MainPage />} />
        <Route path="locations">
          <Route path="new" element={<LocationForm />} />
        </Route>
        <Route path="conferences">
          <Route path="new" element={<ConferenceForm />} />
        </Route>
        <Route path="attendees">
          <Route index element={<AttendeesList />} />
          <Route path="new" element={<AttendConferenceForm />} />
        </Route>
        <Route path="presentations">
          <Route path="new" element={<PresentationForm />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
