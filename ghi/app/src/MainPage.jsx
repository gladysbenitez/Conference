import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';

function ConferenceCard({conference}) {
  return (
        <div  className="card mb-3 shadow">
          <img src={conference.location.pictureUrl} className="card-img-top" />
          <div className="card-body">
            <h5 className="card-title">{conference.name}</h5>
            <h6 className="card-subtitle mb-2 text-muted">
              {conference.location.name}
            </h6>
            <p className="card-text">
              {conference.description}
            </p>
          </div>
          <div className="card-footer">
            {new Date(conference.starts).toLocaleDateString()}
            -
            {new Date(conference.ends).toLocaleDateString()}
          </div>
        </div>
  );
}

const MainPage = () => {
  const [conferences, setConferences] = useState([])

  const fetchData = async () => {
    const url = 'http://localhost:8000/api/locations/';
    const response = await fetch(url);
    if (response.ok) {
      // Get the list of conferences
      const data = await response.json();

      const conferences = data.locations.reduce((accumulator, currentLocation) => {
        const locationConferences = currentLocation.conferences.map(conference =>
          ({...conference,
            location: {
              pictureUrl: currentLocation.picture_url,
              name: currentLocation.name
            }
          }))

        return [...accumulator, ...locationConferences]
      },[])
      setConferences(conferences)
    }
  }

  useEffect(() => {
    fetchData()
  },[])

  return (
    <>
      <div className="px-4 py-5 my-5 mt-0 text-center bg-info">
        <img className="bg-white rounded shadow d-block mx-auto mb-4" src="/logo.svg" alt="" width="600" />
        <h1 className="display-5 fw-bold">Conference GO!</h1>
        <div className="col-lg-6 mx-auto">
          <p className="lead mb-4">
            The only resource you'll ever need to plan an run your in-person or
            virtual conference for thousands of attendees and presenters.
          </p>
          <div className="d-grid gap-2 d-sm-flex justify-content-sm-center">
            <Link to="/attendees/new" className="btn btn-primary btn-lg px-4 gap-3">Attend a conference</Link>
          </div>
        </div>
      </div>
      <div className="container">
        <h2>Upcoming conferences</h2>
        <div className="grid">
          {conferences.map(conference=> {
            return (
              <ConferenceCard key={conference.id} conference={conference} />
            );
          })}
        </div>
      </div>
    </>
  );
}

export default MainPage;
