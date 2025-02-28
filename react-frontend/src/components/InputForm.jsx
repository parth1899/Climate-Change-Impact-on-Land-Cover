import React, { useState } from "react";

const InputForm = ({ onSubmit }) => {
  const [region, setRegion] = useState("");
  const [years, setYears] = useState([]);
  const [classes, setClasses] = useState([]);

  const handleYearChange = (e) => {
    const value = parseInt(e.target.value);
    const isChecked = e.target.checked;

    if (isChecked) {
      setYears([...years, value]);
    } else {
      setYears(years.filter((year) => year !== value));
    }
  };

  const handleClassChange = (e) => {
    const value = e.target.value;
    const isChecked = e.target.checked;

    if (isChecked) {
      setClasses([...classes, value]);
    } else {
      setClasses(classes.filter((cls) => cls !== value));
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Validate inputs
    if (!region) {
      alert("Please enter a region name");
      return;
    }
    if (years.length === 0) {
      alert("Please select at least one year");
      return;
    }
    if (classes.length === 0) {
      alert("Please select at least one concentration class");
      return;
    }

    // Submit form data
    onSubmit({ region, years, classes });
  };

  return (
    <div className="input-section">
      <form onSubmit={handleSubmit}>
        <div className="input-group">
          <label htmlFor="region">Region:</label>
          <input
            type="text"
            id="region"
            placeholder="Enter region name (e.g., Maharashtra)"
            value={region}
            onChange={(e) => setRegion(e.target.value)}
          />
        </div>

        <div className="input-group">
          <label>Years:</label>
          <div className="checkbox-group">
            <label>
              <input
                type="checkbox"
                name="years"
                value="2019"
                onChange={handleYearChange}
              />{" "}
              2019
            </label>
            <label>
              <input
                type="checkbox"
                name="years"
                value="2020"
                onChange={handleYearChange}
              />{" "}
              2020
            </label>
          </div>
        </div>

        <div className="input-group">
          <label>Concentration Classes:</label>
          <div className="checkbox-group">
            <label>
              <input
                type="checkbox"
                name="classes"
                value="low"
                onChange={handleClassChange}
              />{" "}
              Low
            </label>
            <label>
              <input
                type="checkbox"
                name="classes"
                value="medium"
                onChange={handleClassChange}
              />{" "}
              Medium
            </label>
            <label>
              <input
                type="checkbox"
                name="classes"
                value="high"
                onChange={handleClassChange}
              />{" "}
              High
            </label>
          </div>
        </div>

        <button type="submit" className="submit-btn">
          Show Map
        </button>
      </form>
    </div>
  );
};

export default InputForm;
