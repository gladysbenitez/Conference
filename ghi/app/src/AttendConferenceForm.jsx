import React, {useState, useEffect } from 'react';

function AttendConferenceForm() {
  const [conferences, setConferences] = useState([])
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    conference: ''
  })

  const [hasSignedUp, setHasSignedUp] = useState(false)

  const getData = async () => {
    const url = 'http://localhost:8000/api/conferences/';
    const response = await fetch(url);

    if (response.ok) {
      const data = await response.json();
      setConferences(data.conferences);
    }
  }
  
  useEffect(() => {
    getData();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    const locationUrl = `http://localhost:8001${formData.conference}attendees/`;
    
    const fetchConfig = {
      method: "post",
      body: JSON.stringify(formData),
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const response = await fetch(locationUrl, fetchConfig);
    
    if (response.ok) {
      setFormData({
        name: '',
        email: '',
        conference: ''
      });

      setHasSignedUp(true);
    }
  }

  const handleChangeName = (e) => {
    const value = e.target.value;
    const inputName = e.target.name;
    setFormData({
      ...formData,
      [inputName]: value 
    });
  }

  //Allows for the form to display on when a user has not signed in.
  //If a user has signed in, the css class d-none is added to the unneeded piece of the interface

  const formClasses = (!hasSignedUp) ? '' : 'd-none';
  const messageClasses = (!hasSignedUp) ? 'alert alert-success d-none mb-0' : 'alert alert-success mb-0';
  
  return (
    <div className="my-5">
      <div className="row">
        <div className="col col-sm-auto">
          <img width="300" className="bg-white rounded shadow d-block mx-auto mb-4" src="logo.svg" />
        </div>

        <div className="col">
          <div className="card shadow">
            <div className="card-body">

              <form className={formClasses} onSubmit={handleSubmit} id="create-attendee-form">
                <h1 className="card-title">It's Conference Time!</h1>
                <p className="mb-3">
                  Please choose which conference
                  you'd like to attend.
                </p>
                
                <div className="mb-3">
                  <select onChange={handleChangeName} name="conference" id="conference" required>
                    <option value="">Choose a conference</option>
                    {
                      conferences.map(conference => {
                        return (
                          <option key={conference.href} value={conference.href}>{conference.name}</option>
                        )
                      })
                    }
                  </select>
                </div>

                <p className="mb-3">
                  Now, tell us about yourself.
                </p>

                <div className="row">
                  <div className="col">
                    <div className="form-floating mb-3">
                      <input onChange={handleChangeName} required placeholder="Your full name" type="text" id="name" name="name" className="form-control" />
                      <label htmlFor="name">Your full name</label>
                    </div>
                  </div>
                  <div className="col">
                    <div className="form-floating mb-3">
                      <input onChange={handleChangeName} required placeholder="Your email address" type="email" id="email" name="email" className="form-control" />
                      <label htmlFor="email">Your email address</label>
                    </div>
                  </div>
                </div>
                <button className="btn btn-lg btn-primary">I'm going!</button>
              </form>

              <div className={messageClasses} id="success-message">
                Congratulations! You're all signed up!
              </div>

            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AttendConferenceForm;