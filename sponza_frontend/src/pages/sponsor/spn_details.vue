<script setup>
  import Base from "./spn_base.vue";
  import "../../static/sponsor/styles/sponsor_details.css"
  
  import add_logo from "../../static/sponsor/images/add.png";

  import API from "@/router/axios";
  import { onUnmounted,onMounted,ref, reactive,computed } from 'vue';
  import { useRoute } from 'vue-router';
  import Swal from "sweetalert2";

  const route = useRoute();
  const isLoading = ref(false);
  const timeRemaining = ref(""); 
  let interval;
  const isEditing = ref(false);
  const editableDate = ref("");
  const campaignDetails = reactive({
    campaign_id:"",
    campaign_title:"",
    campaign_desc:"",
    campaign_start_date:"",
    campaign_end_date:"",
    campaign_expenses:"",
    campaign_visibility:"",
    campaign_goals:"",
    admin_flag:"",
    admin_flag_time: new Date(),
    campaign_profile_image:"",
    })
  const influencers = ref([]);
  const campSentPending = ref([]);
  const infSentPending = ref([]);
  const influencerSearchQuery = ref('');
  const campSentPendingQuery = ref('');
  const infSentPendingQuery = ref('');

  const filteredInfluencers = computed(() => {
    return influencers.value.filter((inf) =>
      inf.influencer_user_name.toLowerCase().includes(influencerSearchQuery.value.toLowerCase())
    );
  });

  const filteredcampSentPending = computed(() => {
    return campSentPending.value.filter((inf) =>
      inf.influencer_user_name.toLowerCase().includes(campSentPendingQuery.value.toLowerCase())
    );
  });

  const filteredinfSentPending = computed(() => {
    return infSentPending.value.filter((inf) =>
      inf.influencer_user_name.toLowerCase().includes(infSentPendingQuery.value.toLowerCase())
    );
  });

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toISOString().split("T")[0];
  };

  const fetchDetails = async () => {
  try {
    const response = await API.get(`/sponsor/details/${route.params.id}`);
    const data = response.data;

    campaignDetails.campaign_id = data.camp.campaign_id;
    campaignDetails.campaign_title = data.camp.campaign_title;
    campaignDetails.campaign_desc = data.camp.campaign_desc;
    campaignDetails.campaign_start_date = formatDate(data.camp.campaign_start_date);
    campaignDetails.campaign_end_date = formatDate(data.camp.campaign_end_date);
    campaignDetails.campaign_goals = data.camp.campaign_goals;
    campaignDetails.campaign_expenses = data.camp.campaign_expenses;
    campaignDetails.campaign_visibility = data.camp.campaign_visibility;
    campaignDetails.campaign_profile_image = data.camp.campaign_profile_image;
    campaignDetails.admin_flag = data.camp.admin_flag;
    campaignDetails.admin_flag_time = new Date(data.camp.admin_flag_time);

    campSentPending.value=data.camp_sent_pending;
    infSentPending.value=data.inf_sent_pending;
    influencers.value=data.accpted_inf;

    calculateTimeRemaining(); // Initialize the countdown
  } catch (error) {
    console.error(error)
    Swal.fire({
      icon: "error",
      text: "Error fetching campaigns data contact admin",
      confirmButtonText: "Go Back",
    }).then((result) => {
      if (result.isConfirmed) {
        window.location = "/spn/campaigns";
      }
    });
  }
  };

  const updateVisibility = async () => {
    try {
      const response = await API.put(
        `/sponsor/change-details/${campaignDetails.campaign_id}`,
        { campaign_visibility: campaignDetails.campaign_visibility }
      );
    } catch (error) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: error.response?.data?.message || "Failed to update visibility.",
      });
    }
  };

  const startEditing = () => {
    isEditing.value = true;
    editableDate.value = campaignDetails.campaign_end_date;
  };

  const cancelEditing = () => {
    isEditing.value = false;
    editableDate.value = campaignDetails.campaign_end_date;
  };

  const updateEndDate = async () => {
    if (!editableDate.value) {
      Swal.fire({
        icon: "error",
        title: "Invalid Date",
        text: "Please select a valid date.",
      });
      return;
    }

    try {
      const response = await API.put(
        `/sponsor/change-details/${campaignDetails.campaign_id}`,
        {
          campaign_end_date: editableDate.value,
        }
      );

      if (response.data.status === "success") {
        campaignDetails.campaign_end_date = editableDate.value;
        isEditing.value = false;
        // Swal.fire({
        //   icon: "success",
        //   title: "Success",
        //   text: response.data.message,
        // });
      } else {
        throw new Error(response.data.message);
      }
    } catch (error) {
      Swal.fire({
        icon: "error",
        title: "Error",
        text: error.response?.data?.message || error.message,
      });
    }
  };
    
  const showAcceptedDetails = (item) => {
    const title = `Influencer Details`;
    let content = `
        <p><strong>Influencer Name:</strong> ${item.influencer_user_name}</p>
        <p><strong>Niche:</strong> ${item.influencer_niche}</p>
        <p><strong>Email:</strong> ${item.email}</p>
        <p><strong>Amount Paid:</strong> ₹${item.amt}</p>
        <p><strong>Social Media Platform:</strong> <a href="${item.influencer_social_media_link}">${item.influencer_social_media_platform}</a></p>
`

    Swal.fire({
      title: title,
      html: content,
      icon: 'info',
      confirmButtonText: 'OK'
    });
  };

  const calculateTimeRemaining = () => {
    const deleteTime = new Date(campaignDetails.admin_flag_time);
    deleteTime.setHours(deleteTime.getHours() + 24); // 24-hour deletion window

    const now = new Date();
    const timeDiff = deleteTime - now;

    if (timeDiff <= 0) {
      timeRemaining.value = "Campaign has expired";
      clearInterval(interval); // Stop the interval when expired
      return;
    }

    const hours = Math.floor(timeDiff / (1000 * 60 * 60));
    const minutes = Math.floor((timeDiff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((timeDiff % (1000 * 60)) / 1000);

    timeRemaining.value = `${hours} hrs ${minutes} mins ${seconds} secs`;
  }

  const editDetail = (element) => {
    const form = document.getElementById(`change-${element}-form`)
    const span = document.getElementById(`${element}-span`)
    const editIcon =  document.getElementById(`edit-${element}`)
    const saveIcon = document.getElementById(`save-${element}`)
    const cancelIcon = document.getElementById(`cancel-${element}`)
    const input = document.getElementById(`product-${element}-input`)
    span.classList.add("hidden");
    editIcon.classList.add("hidden");

    
    input.dataset.initialValue = input.value.trim();
    input.focus();

    form.classList.remove("hidden"); 
    saveIcon.classList.remove("hidden"); 
    cancelIcon.classList.remove("hidden"); 
  }

  const cancelDetail = (element) => {
      const form = document.getElementById(`change-${element}-form`);
      const span = document.getElementById(`${element}-span`);
      const editIcon = document.getElementById(`edit-${element}`);
      const saveIcon = document.getElementById(`save-${element}`);
      const cancelIcon = document.getElementById(`cancel-${element}`);
      const input = document.getElementById(`product-${element}-input`);

      // Reset title input to its initial value
      input.value = input.dataset.initialValue;

      // Toggle visibility
      span.classList.remove("hidden");
      editIcon.classList.remove("hidden");
      form.classList.add("hidden");
      saveIcon.classList.add("hidden");
      cancelIcon.classList.add("hidden");
  };

  const saveDetail = (element) => {
      const input = document.getElementById(`product-${element}-input`);
      const errorMessage = document.getElementById(`${element}-error-message`);
      const span = document.getElementById(`${element}-span`);
      const editIcon = document.getElementById(`edit-${element}`);
      const saveIcon = document.getElementById(`save-${element}`);
      const cancelIcon = document.getElementById(`cancel-${element}`);
      const form = document.getElementById(`change-${element}-form`);
      const initialValue = input.dataset.initialValue;

      let data; // Declare the variable here

      // Validate input
      if (!input.value.trim()) {
          errorMessage.textContent = `${element} is required`;
          errorMessage.classList.remove("hidden");
          return;
      }
      if (input.value.trim() === initialValue) {
          errorMessage.textContent = "No changes detected";
          errorMessage.classList.remove("hidden");
          return;
      }

      // Clear error messages
      errorMessage.classList.add("hidden");

      // Assign data based on the element type
      if (element === 'title') {
          data = { campaign_title: input.value.trim() };
      } else if (element === 'desc') {
          data = { campaign_desc: input.value.trim() };
      } else if (element === 'goals') {
          data = { campaign_goals: input.value.trim() };
      }

      // Send updated title to backend
      API.put(`/sponsor/change-details/${campaignDetails.campaign_id}`, data)
          .then((response) => {
              const { message, status } = response.data;

              if (status === "success") {
                  // Update UI to reflect changes
                  span.textContent = `${input.value.trim()}`;
                  input.dataset.initialValue = input.value.trim(); // Update initial value

                  // Swal.fire({
                  //     title: "Success",
                  //     text: message,
                  //     icon: "success",
                  //     confirmButtonText: "OK",
                  // });

                  // Toggle visibility
                  span.classList.remove("hidden");
                  editIcon.classList.remove("hidden");
                  form.classList.add("hidden");
                  saveIcon.classList.add("hidden");
                  cancelIcon.classList.add("hidden");
              } else {
                  Swal.fire({
                      title: "Error",
                      text: message || "An unknown error occurred.",
                      icon: "error",
                      confirmButtonText: "OK",
                  });
              }
          })
          .catch((error) => {
              console.error("Error:", error);
              Swal.fire({
                  title: "Error",
                  text: "Failed to update title. Please try again later.",
                  icon: "error",
                  confirmButtonText: "OK",
              });
          });
  };

  const deleteCampaign = async () => {
    try {
      const result = await Swal.fire({
        title: "You are about to delete the Campaign, are you sure?",
        html: `
          <div style="margin-top: 10px;">
            <i class="fa-solid fa-exclamation-triangle" style="color: orange;"></i>
            <span>Consider the checkbox, Deleting all data is not recommended!</span>
          </div>
          <div>
            <input type="checkbox" id="accept-terms">
            <label for="accept-terms">Accept terms and conditions</label>
          </div>   
        `,
        icon: "info",
        showCancelButton: true,
        confirmButtonText: "Yes, delete it!",
        cancelButtonText: "Cancel",
        preConfirm: () => {
          const acceptTerms = document.getElementById("accept-terms").checked;
          if (!acceptTerms) {
            Swal.showValidationMessage(
              "You need to accept the terms and conditions"
            );
            return false;
          }
          return true;
        }
      });

      if (result.isConfirmed) {
        // Assuming `id` is accessible in this scope
        const response = await API.delete(`/sponsor/delete-camp/${route.params.id}`);
        const data = response.data;

        if (data.status === 'success') {
          await Swal.fire({
            title: "Deleted!",
            text: "The campaign has been successfully deleted.",
            icon: "success",
            confirmButtonText: "OK",
          });
          // Redirecting to the campaigns page
          window.location.href = "/spn/campaigns";
        } else {
          await Swal.fire({
            title: "Error",
            text: "Failed to delete the campaign. Please try again later.",
            icon: "error",
            confirmButtonText: "OK",
          });
        }
      }
    } catch (error) {
      console.error("Error deleting campaign:", error);
      await Swal.fire({
        title: "Error",
        text: "An unexpected error occurred. Please try again later.",
        icon: "error",
        confirmButtonText: "OK",
      });
    }
  };

  function showFileUploadAlert() {
    Swal.fire({
      title: 'Upload Campaign Image',
      html: `
        <input type="file" id="campImage" accept="image/png, image/jpg, image/jpeg" class="swal2-file-input" style="display: none;">
        <label for="campImage" class="btn btn-primary">Choose File</label>
        <span id="file-name" style="display:block; margin-top:10px;">No file chosen</span>
      `,
      showCancelButton: true,
      confirmButtonText: 'Upload',
      showLoaderOnConfirm: true,
      preConfirm: async () => {
        const fileInput = document.getElementById("campImage");
        const file = fileInput.files[0];
        if (!file) {
          Swal.showValidationMessage("Please select a file.");
          return false;
        }

        const allowedExtensions = ['png', 'jpg', 'jpeg'];
        const fileExtension = file.name.split('.').pop().toLowerCase();
        if (!allowedExtensions.includes(fileExtension)) {
          Swal.showValidationMessage("Invalid file type. Only PNG, JPG, and JPEG are allowed.");
          return false;
        }

        if (file.size > 2 * 1024 * 1024) { // 2MB limit
          Swal.showValidationMessage("File size exceeds 2MB.");
          return false;
        }

        // Create FormData to send file via Axios
        const formData = new FormData();
        formData.append("camp_image", file);
        formData.append("file", campaignDetails.campaign_profile_image); // Old file

        try {
          // Use Axios instance to send POST request
          const response = await API.put(`/sponsor/update-camp-image/${campaignDetails.campaign_id}`, formData, {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          });

          if (response.data.status !== 'success') {
            throw new Error(response.data.message || 'Failed to upload');
          }

          return response.data;
        } catch (error) {
          Swal.showValidationMessage(`Request failed: ${error.message}`);
          return false;
        }
      },
      allowOutsideClick: () => !Swal.isLoading(),
    }).then((result) => {
      if (result.isConfirmed) {
        // Swal.fire({
        //   title: 'Success!',
        //   text: 'Campaign Image updated successfully!',
        //   icon: 'success',
        // });
        fetchDetails();
      }
    });

    // Show file name after selection
    document.getElementById("campImage").addEventListener("change", function () {
      const fileName = this.files[0]?.name || "No file chosen";
      document.getElementById("file-name").innerText = fileName;
    });
  }

  const removeReq = (inf_id, camp_id) => {
    Swal.fire({
      title: "Are you sure?",
      text: "Do you want to proceed with this Reject?",
      icon: "warning",
      showCancelButton: true,
      confirmButtonColor: "#3085d6",
      cancelButtonColor: "#d33",
      confirmButtonText: "Yes"
    }).then(async (result) => {
      if (result.isConfirmed) {
        try {
          const data = {
            inf_id: inf_id,
            camp_id: camp_id
          };

          // Use Axios instance to send POST request
          const response = await API.delete("/sponsor/rm-ad-req", {
        data: data, // Pass data in the `data` field
        headers: { "Content-Type": "application/json" } // Ensure content type is JSON
      });

          if (response.data.message) {
            Swal.fire({
              title: "Success",
              text: response.data.message,
              icon: "success",
              confirmButtonText: "OK",
              willClose: () => {
                fetchDetails();
              }
            });
          } else {
            Swal.fire({
              title: "Error",
              text: response.data.error || "An unknown error occurred.",
              icon: "error",
              confirmButtonText: "OK",
              willClose: () => {
                location.reload();
              }
            });
          }
        } catch (error) {
          console.error("Error:", error);
          Swal.fire({
            title: "Error",
            text: error.response?.data?.message || "There was an error sending the ad request",
            icon: "error",
            confirmButtonText: "OK",
            willClose: () => {
              location.reload();
            }
          });
        }
      }
    });
  };

  const editSalary = (index) => {
        const form = document.getElementById(`change-salary-form-${index}`)
        const span = document.getElementById(`salary-span-${index}`)
        const editIcon =  document.getElementById(`edit-salary-${index}`)
        const saveIcon = document.getElementById(`save-salary-${index}`)
        const cancelIcon = document.getElementById(`cancel-salary-${index}`)
        const salaryInput = document.getElementById(`product-salary-input-${index}`)
        span.classList.add("hidden");
        editIcon.classList.add("hidden");

        
        salaryInput.dataset.initialValue = salaryInput.value.trim();
        salaryInput.focus();

        form.classList.remove("hidden"); 
        saveIcon.classList.remove("hidden"); 
        cancelIcon.classList.remove("hidden"); 
  };

  const cancelSalary = (index) => {
      const form = document.getElementById(`change-salary-form-${index}`);
      const span = document.getElementById(`salary-span-${index}`);
      const editIcon = document.getElementById(`edit-salary-${index}`);
      const saveIcon = document.getElementById(`save-salary-${index}`);
      const cancelIcon = document.getElementById(`cancel-salary-${index}`);
      const salaryInput = document.getElementById(`product-salary-input-${index}`);

      // Reset salary input to its initial value
      salaryInput.value = salaryInput.dataset.initialValue;

      // Toggle visibility
      span.classList.remove("hidden");
      editIcon.classList.remove("hidden");
      form.classList.add("hidden");
      saveIcon.classList.add("hidden");
      cancelIcon.classList.add("hidden");
  };

  const saveSalary = (index, camp_id) => {
      const salaryInput = document.getElementById(`product-salary-input-${index}`);
      const salaryErrorMessage = document.getElementById(`salary-error-message-${index}`);
      const span = document.getElementById(`salary-span-${index}`);
      const editIcon = document.getElementById(`edit-salary-${index}`);
      const saveIcon = document.getElementById(`save-salary-${index}`);
      const cancelIcon = document.getElementById(`cancel-salary-${index}`);
      const form = document.getElementById(`change-salary-form-${index}`);
      const initialValue = salaryInput.dataset.initialValue;

      // Validate input
      if (!salaryInput.value.trim()) {
          salaryErrorMessage.textContent = "Amount is required";
          salaryErrorMessage.classList.remove("hidden");
          return;
      }
      if (salaryInput.value.trim() === initialValue) {
          salaryErrorMessage.textContent = "No changes detected";
          salaryErrorMessage.classList.remove("hidden");
          return;
      }

      const amount = parseFloat(salaryInput.value.trim());
      if (isNaN(amount) || amount <= 0) {
          salaryErrorMessage.textContent = "Amount must be a positive number";
          salaryErrorMessage.classList.remove("hidden");
          return;
      }

      // Clear error messages
      salaryErrorMessage.classList.add("hidden");

      // Send updated salary to backend
      API.put(`/sponsor/change-salary/${camp_id}`, { salary: salaryInput.value.trim() })
          .then((response) => {
              const { message, status } = response.data;

              if (status === "success") {
                  // Update UI to reflect changes
                  span.textContent = `₹${salaryInput.value.trim()}`;
                  salaryInput.dataset.initialValue = salaryInput.value.trim(); // Update initial value

                  // Swal.fire({
                  //     title: "Success",
                  //     text: message,
                  //     icon: "success",
                  //     confirmButtonText: "OK",
                  // });

                  // Toggle visibility
                  span.classList.remove("hidden");
                  editIcon.classList.remove("hidden");
                  form.classList.add("hidden");
                  saveIcon.classList.add("hidden");
                  cancelIcon.classList.add("hidden");
              } else {
                  Swal.fire({
                      title: "Error",
                      text: message || "An unknown error occurred.",
                      icon: "error",
                      confirmButtonText: "OK",
                  });
              }
          })
          .catch((error) => {
              console.error("Error:", error);
              Swal.fire({
                  title: "Error",
                  text: "Failed to update salary. Please try again later.",
                  icon: "error",
                  confirmButtonText: "OK",
              });
          });
  };

  const showPendingDetails = (inf) => {
    const inf_id = inf.influencer_id;
    const camp_id = campaignDetails.campaign_id;
    const userName = inf.influencer_user_name;
    const niche = inf.influencer_niche;
    const email = inf.email;
    const amt = inf.amt;
    const platform = inf.influencer_social_media_platform;
    const link = inf.influencer_social_media_link;

    let platformIcon = "";
    let platformColor = "";

    if (platform === "youtube") {
      platformIcon = '<i class="fab fa-youtube"></i>';
      platformColor = "red";
    } else if (platform === "twitter") {
      platformIcon = '<i class="fab fa-twitter"></i>';
      platformColor = "#1DA1F2";
    } else if (platform === "instagram") {
      platformIcon = '<i class="fab fa-instagram"></i>';
      platformColor = "#E1306C";
    }

    Swal.fire({
      title: "Influencer Details",
      html: `
          <form style="text-align:left;">
              <p><strong>Username:</strong> ${userName}</p>
              <p><strong>Niche:</strong> ${niche}</p>
              <p><strong>Email:</strong> ${email}</p>
              <p><strong>Social Profile:</strong>
                  <a href="${link}" target="_blank" style="color: ${platformColor};">
                      ${platformIcon}
                  </a>
              </p>
              <p><strong>Requested Amount:</strong> ₹${amt}</p>
          </form>
        `,
      icon: "info",
      showCancelButton: true,
      cancelButtonText: "Close",
      showDenyButton: true,
      showConfirmButton: true,
      confirmButtonText: "Accept",
      denyButtonText: "Reject"
    }).then((result) => {
      if (result.isConfirmed) {
        Swal.fire({
          title: "Are you sure?",
          text: "Do you want to proceed with this Accept?",
          icon: "warning",
          showCancelButton: true,
          confirmButtonColor: "#3085d6",
          cancelButtonColor: "#d33",
          confirmButtonText: "Yes"
        }).then((result) => {
          if (result.isConfirmed) {
            const data = {
              inf_id: inf_id,
              camp_id: camp_id
            };
            API.put("/sponsor/accept-ad-req", data)
              .then((response) => {
                if (response.data.message) {
                  Swal.fire({
                    title: "Success",
                    text: response.data.message,
                    icon: "success",
                    confirmButtonText: "OK",
                    willClose: () => {
                      fetchDetails();
                    }
                  });
                } else if (response.data.unauthorized) {
                  Swal.fire({
                    title: "Unauthorized",
                    icon: "error",
                    willClose: () => {
                      window.location.href = "/";
                    }
                  });
                } else {
                  Swal.fire({
                    title: "Error",
                    text: response.data.error,
                    icon: "error",
                    willClose: () => {
                      location.reload();
                    }
                  });
                }
              })
              .catch((error) => {
                console.error("Error:", error);
                Swal.fire({
                  title: "Error",
                  text: "There was an error sending the ad request",
                  icon: "error",
                  willClose: () => {
                    location.reload();
                  }
                });
              });
          }
        });
      } else if (result.isDenied) {
        Swal.fire({
          title: "Are you sure?",
          text: "Do you want to proceed with this Reject?",
          icon: "warning",
          showCancelButton: true,
          confirmButtonColor: "#3085d6",
          cancelButtonColor: "#d33",
          confirmButtonText: "Yes"
        }).then((result) => {
          if (result.isConfirmed) {
            const data = {
              inf_id: inf_id,
              camp_id: camp_id
            };
            API.delete("/sponsor/rm-ad-req", { 
              data: data
            }).then((response) => {
                if (response.data.message) {
                  Swal.fire({
                    title: "Success",
                    text: response.data.message,
                    icon: "success",
                    confirmButtonText: "OK",
                    willClose: () => {
                      fetchDetails();
                    }
                  });
                } else if (response.data.unauthorized) {
                  Swal.fire({
                    title: "Unauthorized",
                    icon: "error",
                    willClose: () => {
                      window.location.href = "/";
                    }
                  });
                } else {
                  Swal.fire({
                    title: "Error",
                    text: response.data.error,
                    icon: "error"
                  });
                }
              })
              .catch((error) => {
                console.error("Error:", error);
                Swal.fire({
                  title: "Error",
                  text: "There was an error sending the ad request",
                  icon: "error"
                });
              });
          }
        });
      }
    });
  };

  const createAdRequest = () => {
    let adInfluencer;
    Swal.fire({
      title: "Create New Ad Request",
      html: `
                    <input id="ad-payment" class="swal2-input" placeholder="Payment">
                    <input id="ad-influencer" class="swal2-input" placeholder="Search Influencer" autocomplete="off">
                    <ul id="influencer-suggestions" style="list-style: none; padding: 0; margin-top: 5px;"></ul>
                `,
      showCancelButton: true,
      confirmButtonText: "Submit",
      didOpen: () => {
        const influencerInput = document.getElementById("ad-influencer");
        const suggestionsList = document.getElementById("influencer-suggestions");

        influencerInput.addEventListener("input", function () {
          const query = influencerInput.value;
          if (query.length > 0) {
            // Use API instance for the POST request
            API.post("/sponsor/search-inf", { query: query })
              .then((response) => {
                const data = response.data;
                suggestionsList.innerHTML = "";

                data.users.forEach((user) => {
                  const userBox = document.createElement("li");
                  userBox.classList.add("influencer-box");

                  userBox.innerHTML = `
                                        <div class="influencer-avatar" style="background-image: url('${user.image}');"></div>
                                        <div class="influencer-info">
                                            <h4><b>${user.username}</b></h4>
                                            <p>${user.email || "No email provided"}</p>
                                        </div>
                                    `;
                  userBox.addEventListener("click", function () {
                    influencerInput.value = user.username;
                    suggestionsList.innerHTML = "";
                    adInfluencer = user.id;
                  });

                  suggestionsList.appendChild(userBox);
                });
              })
              .catch((error) => {
                console.error("Error fetching data:", error);
              });
          } else {
            suggestionsList.innerHTML = "";
          }
        });
      },
      preConfirm: () => {
        const adPayment = document.getElementById("ad-payment").value;

        if (!adPayment || !adInfluencer) {
          Swal.showValidationMessage("Please fill in all fields");
          return false;
        }

        if (isNaN(adPayment) || adPayment <= 0) {
          Swal.showValidationMessage("Payment must be a number");
          return false;
        }

        return {
          adPayment: adPayment,
          adInfluencerid: adInfluencer
        };
      }
    }).then((result) => {
      if (result.isConfirmed) {
        const adData = result.value;

        // Use API instance for the POST request
        API.post(`/sponsor/send-ad-request/${campaignDetails.campaign_id}`, adData)
          .then((response) => {
            const data = response.data;
            if (data.message) {
              Swal.fire({
                title: "Success",
                text: data.message,
                icon: "success",
                confirmButtonText: "OK",
                willClose: () => {
                  fetchDetails();
                }
              });
            } else {
              Swal.fire({
                title: "Error",
                text: data.error,
                icon: "error"
              });
            }
          })
          .catch((error) => {
            console.error("Error:", error);
            Swal.fire({
              title: "Error",
              text: "There was an error sending the ad request",
              icon: "error"
            });
          });
      }
    });
  };

  onMounted(() => {
    fetchDetails();
    interval = setInterval(calculateTimeRemaining, 1000); 
  });

  onUnmounted(() => {
    clearInterval(interval); 
  });

</script>


<template>
    <Base>
        <div v-if="isLoading" class="loading-overlay">
            <div class="spinner"></div>
        </div>

        <h5 v-if="campaignDetails.admin_flag === 'True'" style="color:red" class="h5 total-expenses">
          This Campaign has been flagged by admin. It will be deleted in 
          <span>{{ timeRemaining }}</span>. Contact admin for appeal.
        </h5>

        <h1 class="h3 mb-4 text-gray-800 total-expenses">Campaign Total Expenses: {{campaignDetails.campaign_expenses}}</h1>

        <div class="top-content">
          <div class="left-content">
              <div class="top">
                  <h1 class="h3 mb-4 text-gray-800" style="margin-left: 6vh; width: auto;">Campaign Details :</h1>
                <button id="delete-campaign" class="delete-button" @click="deleteCampaign">Delete</button>
              </div>
              <div class="details-top">
              <div id="product-name-container">
                  <h4><b>Name:</b>     <span :id="`title-span`">{{ campaignDetails.campaign_title }}</span>
              <i :id="`edit-title`" @click="editDetail('title')" class="edit-icon fa-regular fa-pen-to-square" data-target="title"></i>
              <form :id="`change-title-form`" class="hidden">
                <input type="text" :id="`product-title-input`" :value="campaignDetails.campaign_title"/>
                <i :id="`save-title`" @click.prevent="saveDetail('title')" class="save-icon fa-solid fa-check "></i>
                <i :id="`cancel-title`" @click.prevent="cancelDetail('title')" class="cancel-icon fa-solid fa-xmark hidden"
          ></i>
                <div :id="`title-error-message`" class="error-message hidden"></div>
              </form>
                  </h4>
              </div>

              <div id="description-container">
                  <h4><b>Description:</b>     <span :id="`desc-span`">{{ campaignDetails.campaign_desc }}</span>
              <i :id="`edit-desc`" @click="editDetail('desc')" class="edit-icon fa-regular fa-pen-to-square" data-target="desc"></i>
              <form :id="`change-desc-form`" class="hidden">
                <input type="text" :id="`product-desc-input`" :value="campaignDetails.campaign_desc"/>
                <i :id="`save-desc`" @click.prevent="saveDetail('desc')" class="save-icon fa-solid fa-check "></i>
                <i :id="`cancel-desc`" @click.prevent="cancelDetail('desc')" class="cancel-icon fa-solid fa-xmark hidden"
          ></i>
                <div :id="`desc-error-message`" class="error-message hidden"></div>
              </form>
                  </h4>
              </div>
  <div id="end-date-container">
    <h4>
      <b>End Date:</b>
      <span v-if="!isEditing">{{ campaignDetails.campaign_end_date }}</span
        >
        <i
        id="edit-end-date"
        class="edit-icon fa-regular fa-pen-to-square"
        v-if="!isEditing"
        @click="startEditing"
      ></i>
      <div v-else>
      <input
        type="date"
        v-model="editableDate"
        :min="campaignDetails.campaign_start_date"
      />
        <i @click="updateEndDate" class="save-icon fa-solid fa-check "></i>
                <i @click="cancelEditing" class="cancel-icon fa-solid fa-xmark"
          ></i>
      </div>
    </h4>
  </div>

  <div id="visiblity-container">
    
     <h4><b>Campaign Visibility:</b></h4>
  <div class="switch-container">
    <span class="label-text left">Public</span>
    <label class="switch">
      <input
        type="checkbox"
        v-model="campaignDetails.campaign_visibility"
        @change="updateVisibility"
      />
      <span class="slider"></span>
    </label>
    <span class="label-text right">Private</span>
  </div>
  </div>

              <div id="goals-container">
                  <h4><b>Goals:</b>     <span :id="`goals-span`">{{ campaignDetails.campaign_goals }}</span>
              <i :id="`edit-goals`" @click="editDetail('goals')" class="edit-icon fa-regular fa-pen-to-square" data-target="goals"></i>
              <form :id="`change-goals-form`" class="hidden">
                <input type="text" :id="`product-goals-input`" :value="campaignDetails.campaign_goals"/>
                <i :id="`save-goals`" @click.prevent="saveDetail('goals')" class="save-icon fa-solid fa-check "></i>
                <i :id="`cancel-goals`" @click.prevent="cancelDetail('goals')" class="cancel-icon fa-solid fa-xmark hidden"
          ></i>
                <div :id="`goals-error-message`" class="error-message hidden"></div>
              </form>
                  </h4>
              </div>
          </div>
          </div>
          <div class="right-content">
              <img class="campaigns-image" :src="campaignDetails.campaign_profile_image" alt="campaigns-image"
                  style="width: 200px; height: 200px; border-radius: 100%;">
              <button @click="showFileUploadAlert"
                  class="btn btn-primary ml-4 update" id="updateButton">Update</button>
          </div>
        </div>

        <div class="details" v-if="influencers.length">
        <div class="top-details influencers-search">
          <h1 class="h3 mb-4 text-gray-800">Accepted Influencers:</h1>
          <form @submit.prevent="performInfluencerSearch">
            <input v-model="influencerSearchQuery" type="search" class="search-text" placeholder="Search the Influencer" autocomplete="off" />
          </form>
        </div>
        <div v-if="filteredInfluencers.length">
          <div class="detail-box" id="influencers-detail-box">
            <div v-for="inf in filteredInfluencers" :key="inf.influencer_id" class="influencer-box">
              <img :src="inf.influencer_profile_image" alt="Profile Image" class="profile-img" />
              <h5>{{ inf.influencer_user_name }}</h5>
              <button @click="showAcceptedDetails(inf)" class="view view-influencer">View</button>
              <button @click="removeReq(inf.influencer_id,campaignDetails.campaign_id)" class="remove">Remove</button>
            </div>
          </div>
        </div>
        <div v-else class="no-matches">No matched data</div>
        </div>
        <div v-else>
            <h1 class="h3 mb-4 text-gray-800"
                style="margin-bottom: 3vh !important; margin-top: 3vh;padding-left: 3rem;">No Influencers is assigned
                for this Campaign</h1>
        </div>

        <div class="details" v-if="campSentPending.length">
          <div class="top-details influencers-search">
            <h1 class="h3 mb-4 text-gray-800">Request Sent:</h1>
            <form @submit.prevent="performInfluencerSearch">
              <input v-model="campSentPendingQuery" type="search" class="search-text" placeholder="Search the Influencer" autocomplete="off" />
            </form>
          </div>
          <div v-if="filteredcampSentPending.length">
            <div class="detail-box" id="influencers-detail-box">
              <div v-for="(inf,index) in filteredcampSentPending" :key="inf.influencer_id" class="influencer-box">
                <img :src="inf.influencer_profile_image" alt="Profile Image" class="profile-img" />
                <h5>{{ inf.influencer_user_name }}</h5>
                <div>
                  <span class="salary" :id="`salary-span-${index}`">₹{{ inf.camp_pay }}</span>
                  <i :id="`edit-salary-${index}`" @click="editSalary(index)" class="edit-icon fa-regular fa-pen-to-square" data-target="salary"></i>
                  <form :id="`change-salary-form-${index}`" class="hidden">
                    <input type="text" :id="`product-salary-input-${index}`" :value="inf.camp_pay"/>
                    <i :id="`save-salary-${index}`" @click.prevent="saveSalary(index,inf.main_id)" class="save-icon fa-solid fa-check "></i>
                    <i :id="`cancel-salary-${index}`" @click.prevent="cancelSalary(index)" class="cancel-icon fa-solid fa-xmark hidden"
              ></i>
                    <div :id="`salary-error-message-${index}`" class="error-message hidden"></div>
                  </form>
                </div>
                <button @click="removeReq(inf.influencer_id,campaignDetails.campaign_id)" class="remove">Remove</button>
              </div>
            </div>
          </div>
          <div v-else class="no-matches">No matched data</div>
        </div>
        <div v-else>
                  <h1 class="h3 mb-0 text-gray-800 no-request-recieved"
                      style="margin-bottom: 1vh !important; margin-top: 10vh !important;padding-left: 3rem;">No Request Sent
                  </h1>
        </div>

        <div class="details" v-if="infSentPending.length">
          <div class="top-details influencers-search">
            <h1 class="h3 mb-4 text-gray-800">Request Recieved:</h1>
            <form @submit.prevent="performInfluencerSearch">
              <input v-model="infSentPendingQuery" type="search" class="search-text" placeholder="Search the Influencer" autocomplete="off" />
            </form>
          </div>
          <div v-if="filteredinfSentPending.length">
            <div class="detail-box" id="influencers-detail-box">
              <div v-for="inf in filteredinfSentPending" :key="inf.influencer_id" class="influencer-box">
                <img :src="inf.influencer_profile_image" alt="Profile Image" class="profile-img" />
                <h5>{{ inf.influencer_user_name }}</h5>
                <button @click="showPendingDetails(inf)" class="view view-influencer">View</button>
              </div>
            </div>
          </div>
          <div v-else class="no-matches">No matched data</div>
        </div>
        <div v-else>
                  <h1 class="h3 mb-0 text-gray-800 no-request-recieved"
                      style="margin-bottom: -3vh !important; margin-top: 3vh;padding-left: 3rem;">No Request Recieved
                  </h1>
        </div>
          
        <div class="create-detail">
              <h1 class="h3 mb-4 text-gray-800">Create New ad Request</h1>
              <img @click="createAdRequest" :src="add_logo"
                  style="width: 120px; height: 120px; border-radius: 100%;" class="add-ad_request-image">
        </div>
    </Base>
</template>

<style scoped>
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5); 
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999; 
}

.spinner {
  border: 8px solid rgba(255, 255, 255, 0.3); 
  border-top: 8px solid #ffffff; 
  border-radius: 50%;
  width: 60px;
  height: 60px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>


