package services

import (
	"github.com/erc-kg/backend-go/internal/repository"
	"github.com/erc-kg/backend-go/internal/config"
)

type AuthService struct {
	userRepo *repository.UserRepository
	jwtConfig config.JWTConfig
}

func NewAuthService(userRepo *repository.UserRepository, jwtConfig config.JWTConfig) *AuthService {
	return &AuthService{
		userRepo:   userRepo,
		jwtConfig:  jwtConfig,
	}
}
