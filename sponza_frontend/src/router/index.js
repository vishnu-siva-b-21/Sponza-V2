import { createRouter, createWebHistory } from "vue-router";
import Swal from "sweetalert2";

const isAuthenticated = () => {
  const token = localStorage.getItem("accessToken");
  return !!token;
};

const hasRole = (requiredRole) => {
  const userRole = localStorage.getItem("userRole");
  return userRole === requiredRole;
};

const showAlert = (message) => {
  Swal.fire({
    icon: "warning",
    title: "Access Denied",
    text: message,
    confirmButtonText: "OK"
  });
};

const routes = [
  {
    path: "/",
    component: () => import("@/pages/main/home.vue")
  },
  {
    path: "/user-reset-password",
    component: () => import("@/pages/main/reset_password.vue")
  },
  {
    path: "/spn/monthly-report",
    component: () => import("@/pages/sponsor/spn_monthly_report.vue")
  },
  {
    path: "/admin/dashboard",
    component: () => import("@/pages/admin/admin_dashboard.vue"),
    beforeEnter: (to, from, next) => {
      if (isAuthenticated()) {
        if (hasRole("admin")) {
          next();
        } else {
          showAlert("You do not have permission to access this page.");
          next("/");
        }
      } else {
        showAlert("Please log in to access this page.");
        next("/");
      }
    }
  },
  {
    path: "/admin/find",
    component: () => import("@/pages/admin/admin_find.vue"),
    beforeEnter: (to, from, next) => {
      if (isAuthenticated()) {
        if (hasRole("admin")) {
          next();
        } else {
          showAlert("You do not have permission to access this page.");
          next("/");
        }
      } else {
        showAlert("Please log in to access this page.");
        next("/");
      }
    }
  },
  {
    path: "/inf/dashboard",
    component: () => import("@/pages/influencer/inf_dashboard.vue"),
    beforeEnter: (to, from, next) => {
      if (isAuthenticated()) {
        if (hasRole("influencer")) {
          next();
        } else {
          showAlert("You do not have permission to access this page.");
          next("/");
        }
      } else {
        showAlert("Please log in to access this page.");
        next("/");
      }
    }
  },
  {
    path: "/inf/campaigns/:id?",
    component: () => import("@/pages/influencer/inf_campaigns.vue"),
    beforeEnter: (to, from, next) => {
      if (isAuthenticated()) {
        if (hasRole("influencer")) {
          next();
        } else {
          showAlert("You do not have permission to access this page.");
          next("/");
        }
      } else {
        showAlert("Please log in to access this page.");
        next("/");
      }
    }
  },
  {
    path: "/inf/requests",
    component: () => import("@/pages/influencer/inf_requests.vue"),
    beforeEnter: (to, from, next) => {
      if (isAuthenticated()) {
        if (hasRole("influencer")) {
          next();
        } else {
          showAlert("You do not have permission to access this page.");
          next("/");
        }
      } else {
        showAlert("Please log in to access this page.");
        next("/");
      }
    }
  },
  {
    path: "/inf/profile",
    component: () => import("@/pages/influencer/inf_profile.vue"),
    beforeEnter: (to, from, next) => {
      if (isAuthenticated()) {
        if (hasRole("influencer")) {
          next();
        } else {
          showAlert("You do not have permission to access this page.");
          next("/");
        }
      } else {
        showAlert("Please log in to access this page.");
        next("/");
      }
    }
  },
  {
    path: "/spn/dashboard",
    component: () => import("@/pages/sponsor/spn_dashboard.vue"),
    beforeEnter: (to, from, next) => {
      if (isAuthenticated()) {
        if (hasRole("sponsor")) {
          next();
        } else {
          showAlert("You do not have permission to access this page.");
          next("/");
        }
      } else {
        showAlert("Please log in to access this page.");
        next("/");
      }
    }
  },
  {
    path: "/spn/profile",
    component: () => import("@/pages/sponsor/spn_profile.vue"),
    beforeEnter: (to, from, next) => {
      if (isAuthenticated()) {
        if (hasRole("sponsor")) {
          next();
        } else {
          showAlert("You do not have permission to access this page.");
          next("/");
        }
      } else {
        showAlert("Please log in to access this page.");
        next("/");
      }
    }
  },
  {
    path: "/spn/details/:id",
    name: "CampaignDetails",
    component: () => import("@/pages/sponsor/spn_details.vue"),
    beforeEnter: (to, from, next) => {
      if (isAuthenticated()) {
        if (hasRole("sponsor")) {
          next();
        } else {
          showAlert("You do not have permission to access this page.");
          next("/");
        }
      } else {
        showAlert("Please log in to access this page.");
        next("/");
      }
    }
  },
  {
    path: "/spn/campaigns",
    component: () => import("@/pages/sponsor/spn_campaigns.vue"),
    beforeEnter: (to, from, next) => {
      if (isAuthenticated()) {
        if (hasRole("sponsor")) {
          next();
        } else {
          showAlert("You do not have permission to access this page.");
          next("/");
        }
      } else {
        showAlert("Please log in to access this page.");
        next("/");
      }
    }
  },
  {
    path: "/:catchAll(.*)",
    redirect: "/"
  }
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
});

export default router;
