export const validateCampaignFields = (data) => {
  let errors = []

  if (!data.email_group.length) {
    errors.push('Select atleast one email group for recipients.')
  }

  if (!data.subject) {
    errors.push('Subject is required.')
  }

  if (data.content_type == 'Rich Text' && !data.message.length) {
    errors.push('Message is required.')
  }
  if (data.content_type == 'Markdown' && !data.message_md.length) {
    errors.push('Message is required.')
  }
  if (data.content_type == 'HTML' && !data.message_html.length) {
    errors.push('Message is required.')
  }

  if (data.schedule_sending && !data.schedule_send) {
    errors.push('Schedule time is required')
  }

  return errors
}
