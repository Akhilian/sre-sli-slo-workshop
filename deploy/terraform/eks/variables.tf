variable "region" {
  description = "Région AWS."
  type        = string
  default     = "eu-west-3"
}

variable "cluster_name" {
  description = "Nom du cluster EKS."
  type        = string
  default     = "docshare"
}

variable "kubernetes_version" {
  description = "Version de Kubernetes du plan de contrôle."
  type        = string
  default     = "1.35"
}

variable "node_instance_type" {
  description = "Type d'instance des nœuds (le calcul du nombre de nœuds suppose 4 vCPU)."
  type        = string
  default     = "m6i.xlarge"
}

variable "teams" {
  description = "Nombre d'équipes de la séance ; le nombre de nœuds en est déduit."
  type        = number
  default     = 1

  validation {
    condition     = var.teams >= 1 && var.teams <= 12 && floor(var.teams) == var.teams
    error_message = "teams doit être un entier entre 1 et 12."
  }
}

variable "api_allowed_cidrs" {
  description = "Plages autorisées vers l'API Kubernetes (IP de la salle, ex. [\"203.0.113.10/32\"]). Les participants utilisent leur kubeconfig depuis ces adresses."
  type        = list(string)

  validation {
    condition     = length(var.api_allowed_cidrs) > 0 && !contains(var.api_allowed_cidrs, "0.0.0.0/0")
    error_message = "Indiquez au moins une plage précise, 0.0.0.0/0 est refusé."
  }
}
