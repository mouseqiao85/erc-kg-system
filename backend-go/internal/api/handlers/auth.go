package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/erc-kg/backend-go/internal/services"
)

type AuthHandler struct {
	authService *services.AuthService
}

func NewAuthHandler(authService *services.AuthService) *AuthHandler {
	return &AuthHandler{authService: authService}
}

func (h *AuthHandler) Register(c *gin.Context) {
	// TODO: Implement registration
	c.JSON(http.StatusOK, gin.H{"message": "register"})
}

func (h *AuthHandler) Login(c *gin.Context) {
	// TODO: Implement login
	c.JSON(http.StatusOK, gin.H{"message": "login"})
}

func (h *AuthHandler) Logout(c *gin.Context) {
	// TODO: Implement logout
	c.JSON(http.StatusOK, gin.H{"message": "logout"})
}

func (h *AuthHandler) RefreshToken(c *gin.Context) {
	// TODO: Implement refresh token
	c.JSON(http.StatusOK, gin.H{"message": "refresh token"})
}
