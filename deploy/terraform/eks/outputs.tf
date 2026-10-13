output "cluster_name" {
  value = module.eks.cluster_name
}

output "kubeconfig_command" {
  description = "Crée le contexte kubectl de l'animateur, à utiliser ensuite avec deploy/scripts/setup.sh."
  value       = "aws eks update-kubeconfig --region ${var.region} --name ${module.eks.cluster_name}"
}
