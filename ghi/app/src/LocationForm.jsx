import React, { useEffect, useState } from 'react';

function LocationForm () {
  const [states, setStates] = useState([])
  const [formData, setFormData] = useState({
    name: '',
    room_count: '',
    city: '',
    state: ''
  })

  const getData = async () => {
    const url = 'http://localhost:8000/api/states/';
    const response = await fetch(url);
    console.log(response)

    if (response.ok) {
      const data = await response.json();
      setStates(data.states);
    }
  }

  useEffect(()=> {
    getData();
  }, [])

  const handleSubmit = async (event) => {
    event.preventDefault();

    const locationUrl = 'http://localhost:8000/api/locations/';

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
        room_count: '',
        city: '',
        state: ''
      });
    }
  }

  const handleFormChange = (e) => {
    const value = e.target.value;
    const inputName = e.target.name;
    setFormData({
      //Previous form data is spread (i.e. copied) into our new state object
      ...formData,

      //On top of the that data, we add the currently engaged input key and value
      [inputName]: value
    });
  }

  return (
    <div className="row">
      <div className="offset-3 col-6">
        <div className="shadow p-4 mt-4">
          <h1>Create a new location</h1>
          <form onSubmit={handleSubmit} id="create-location-form">
            <div className="form-floating mb-3">
              <input value={formData.name} onChange={handleFormChange} placeholder="Name" required type="text" name="name" id="name" className="form-control" />
              <label htmlFor="name">Name</label>
            </div>
            <div className="form-floating mb-3">
              <input value={formData.room_count} onChange={handleFormChange} placeholder="Room count" required type="number" name="room_count" id="room_count" className="form-control" />
              <label htmlFor="room_count">Room count</label>
            </div>
            <div className="form-floating mb-3">
              <input value={formData.city} onChange={handleFormChange} placeholder="City" required type="text" name="city" id="city" className="form-control" />
              <label htmlFor="city">City</label>
            </div>
            <div className="mb-3">
              <select value={formData.state} onChange={handleFormChange} required name="state" id="state" className="form-select">
                <option value="">Choose a state</option>
                {Object.keys(states).map(state => {
                  return (
                    <option key={state} value={state}>
                      {state}
                    </option>
                  );
                })}
              </select>
            </div>
            <button className="btn btn-primary">Create</button>
          </form>
        </div>
      </div>
    </div>
  );
}

export default LocationForm;
