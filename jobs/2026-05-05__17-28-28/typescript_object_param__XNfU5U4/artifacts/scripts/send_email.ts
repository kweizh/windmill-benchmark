export async function main(
  recipient: { email: string; name: string },
  subject: string,
  body: string,
  dry_run: boolean = true
) {
  return {
    to: `${recipient.name} <${recipient.email}>`,
    subject,
    body,
    dry_run,
    sent: !dry_run,
    preview: `To: ${recipient.name} <${recipient.email}>\nSubject: ${subject}\n\n${body}`,
  };
}
