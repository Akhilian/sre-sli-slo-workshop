{{- define "docshare.labels" -}}
app.kubernetes.io/part-of: docshare
docshare.workshop/team: {{ .Values.team | default .Release.Namespace | quote }}
{{- end }}

{{- define "docshare.image" -}}
{{ .Values.image.repository }}:{{ .Values.image.tag }}
{{- end }}

{{- define "docshare.env" -}}
- name: REDIS_URL
  value: redis://redis:6379/0
- name: DATABASE_URL
  value: postgresql://docshare:{{ .Values.postgres.password }}@postgres:5432/docshare
{{- end }}
