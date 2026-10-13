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
  description = "Type d'instance des nœuds (4 vCPU et 16 Go suffisent pour 4 équipes avec 3 nœuds)."
  type        = string
  default     = "m6i.xlarge"
}

variable "node_count" {
  description = "Nombre de nœuds."
  type        = number
  default     = 3
}

variable "api_allowed_cidrs" {
  description = "Plages autorisées vers l'API Kubernetes (IP de la salle, ex. [\"203.0.113.10/32\"]). Les participants utilisent leur kubeconfig depuis ces adresses."
  type        = list(string)

  validation {
    condition     = length(var.api_allowed_cidrs) > 0 && !contains(var.api_allowed_cidrs, "0.0.0.0/0")
    error_message = "Indiquez au moins une plage précise, 0.0.0.0/0 est refusé."
  }
}
