<script setup>
import Swal from "sweetalert2";
import API from "@/router/axios";
import { onMounted } from 'vue';
import "../../static/common/styles/common_main.css";
import "../../static/common/scripts/common_main.js";
import admin_logo from "../../static/admin/images/profile_pics/admin.png";


onMounted(() => {
  const urlParams = new URLSearchParams(window.location.search);
  if (urlParams.get("login") === "success") {
    Swal.fire({
      title: "Login Successful",
      icon: "success",
      confirmButtonText: "OK",
    });
  } else if (urlParams.get("authenticated") === "success") {
    Swal.fire({
      title: "You are already authenticated and Logged in",
      icon: "success",
      confirmButtonText: "OK",
    });
  }
  const newUrl = window.location.origin + window.location.pathname;
  window.history.replaceState({}, document.title, newUrl);
});


const logout = async () => {
  try {
    await API.post("/logout", {});
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("userRole");
    window.location.href = "/?logout=success";
  } catch (error) {
    console.error("Error during logout:", error);
    Swal.fire({
      title: "Error",
      text: "An error occurred during logout. Please try again.",
      icon: "error",
      confirmButtonText: "OK",
    });
  }
};

</script>

<template>
  <div id="wrapper">
    <ul class="navbar-nav bg-gradient-primary sidebar sidebar-dark accordion" id="accordionSidebar">
      <a class="sidebar-brand d-flex align-items-center justify-content-center" href="#">
        <div class="sidebar-brand-icon rotate-n-15">
          <i class="fas fa-laugh-wink"></i>
        </div>
        <div class="sidebar-brand-text mx-3">Admin</div>
      </a>
      <hr class="sidebar-divider my-0" />

      <li class="nav-item">
        <a class="nav-link" href="/admin/dashboard">
          <i class="fas fa-fw fa-tachometer-alt"></i>
          <span>Dashboard</span>
        </a>
      </li>
      <hr class="sidebar-divider" />

      <li class="nav-item">
        <a class="nav-link collapsed" href="/admin/find">
          <i class="fas fa-fw fa-wrench"></i>
          <span>The Database</span>
        </a>
      </li>
      <hr class="sidebar-divider" />

      <div class="text-center d-none d-md-inline">
        <button class="rounded-circle border-0" id="sidebarToggle"></button>
      </div>
    </ul>

    <div id="content-wrapper" class="d-flex flex-column">
      <div id="content">
        <nav class="navbar navbar-expand navbar-light bg-white topbar mb-4 static-top shadow">
          <button id="sidebarToggleTop" class="btn btn-link d-md-none rounded-circle mr-3">
            <i class="fa fa-bars"></i>
          </button>
          <ul class="navbar-nav ml-auto">
            <li class="nav-item dropdown no-arrow">
              <a
                class="nav-link dropdown-toggle"
                href="#"
                id="userDropdown"
                role="button"
                data-toggle="dropdown"
                aria-haspopup="true"
                aria-expanded="false"
              >
                <span class="mr-2 d-none d-lg-inline text-gray-600 small">The Admin</span>
                <img class="img-profile rounded-circle" :src="admin_logo" />
              </a>
              <div class="dropdown-menu dropdown-menu-right shadow animated--grow-in" aria-labelledby="userDropdown">
                <a class="dropdown-item" href="#" data-toggle="modal" data-target="#logoutModal">
                  <i class="fas fa-sign-out-alt fa-sm fa-fw mr-2 text-gray-400"></i>
                  Logout
                </a>
              </div>
            </li>
          </ul>
        </nav>

        <slot></slot>

        <a class="scroll-to-top rounded" href="#">
          <i class="fas fa-angle-up"></i>
        </a>

        <div
          class="modal fade"
          id="logoutModal"
          tabindex="-1"
          role="dialog"
          aria-labelledby="exampleModalLabel"
          aria-hidden="true"
        >
          <div class="modal-dialog" role="document">
            <div class="modal-content">
              <div class="modal-header">
                <h5 class="modal-title" id="exampleModalLabel">Ready to Leave?</h5>
                <button class="close" type="button" data-dismiss="modal" aria-label="Close">
                  <span aria-hidden="true">×</span>
                </button>
              </div>
              <div class="modal-body">Select "Logout" below if you are ready to end your current session.</div>
              <div class="modal-footer">
                <button class="btn btn-secondary" type="button" data-dismiss="modal">Cancel</button>
                <a class="btn btn-primary" @click.prevent="logout">Logout</a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
