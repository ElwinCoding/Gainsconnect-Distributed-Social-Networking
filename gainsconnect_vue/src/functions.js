import axios from "axios";
import api from '@/services/api';

//setAxiosAuthToken(): this function retrieves the JWT access token from localStorage and sets it in Axios' default Authorization header. 
    //this will make sure that any request made after this has the token attached.
export function setAxiosAuthToken() {
    const token = localStorage.getItem('access_token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = 'Bearer ' + token;
    }
}

/** 
 * Sends a post request to create a follow request
 * @param {String} senderID - id of sender
 * @param {String} receiverID - id of receiver
 * 
 * @returns {Promise<Object>} - response data from server
*/
export async function follow(actor, object) {
  try {
    const response = await api.post('/follow/request/', {
      actor: actor,
      object: object
    });
    return response.data;
  } catch (error) {
    console.error("Error creating follow request");
    throw error;
  }
}

/**
 * Gets a list of who the author is following
 * @param {String} authorID - id of author
 * 
 * @returns {Promise<Object>} - list of author objects
 */
export async function getFollowingList(authorID) {
  try{
    const response = await api.get(`/follow/list/${authorID}/following`);
    return response.data;
  } catch (error) {
    console.log("Failed getting following list");
    throw error;
  }
}

/**
 * Refreshes token if expired
 */
export async function refreshToken(authorStore) {
  try {
    const refreshToken = localStorage.getItem("refresh_token"); // Get the refresh token from localStorage
    const response = await api.post(
      "/api/token/refresh/",
      {
        refresh: refreshToken,
      }
    );
    // Update the access token in the store
    authorStore.accessToken = response.data.access;
    localStorage.setItem("accessToken", response.data.access); // Store the new access token
  } catch (error) {
    console.error("Error refreshing token:", error);
  }
};

export function formatDate(dateString) {
  const options = { year: "numeric", month: "long", day: "numeric" };
  return new Date(dateString).toLocaleDateString(undefined, options);
};