package services

type UserService struct{}
func NewUserService(_ interface{}) *UserService { return &UserService{} }

type ProjectService struct{}
func NewProjectService(_ interface{}) *ProjectService { return &ProjectService{} }

type DocumentService struct{}
func NewDocumentService(_ interface{}) *DocumentService { return &DocumentService{} }

type EntityService struct{}
func NewEntityService(_ interface{}) *EntityService { return &EntityService{} }

type GraphService struct{}
func NewGraphService(_ interface{}) *GraphService { return &GraphService{} }

type PythonService struct{}
func NewPythonService(_ string) *PythonService { return &PythonService{} }
