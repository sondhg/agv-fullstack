//from 0 to 19
export const parkingNodes = Array.from({ length: 20 }, (_, index) => index);

//from 0 to 19
export const endPoints = Array.from({ length: 20 }, (_, index) => index);

export const loadNames = ["stone", "wood", "iron"];

export const agvIDs = Array.from({ length: 4 }, (_, index) =>
  (index + 1).toString(),
);

export const guidanceTypes = ["Line Following", "Computer Vision"];

// Ensure loadNames is treated as a tuple with at least one string for enum validation in forms
export const loadNamesEnum = loadNames as [string, ...string[]];
