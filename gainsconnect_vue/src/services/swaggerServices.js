import axios from 'axios';

export const fetchSwaggerJSON = async () => {
  try {
    const response = await axios.get('http://localhost:8000/swagger.json');
    return response.data;
  } catch (error) {
    console.error("Error fetching Swagger JSON:", error);
    throw error;
  }
};