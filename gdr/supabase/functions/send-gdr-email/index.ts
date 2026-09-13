// Supabase Edge Function: send-gdr-email
// Required server-side secrets:
// RESEND_API_KEY
// GDR_FROM_EMAIL  e.g. notifications@gdrnetwork.org
// GDR_ADMIN_EMAIL e.g. admin@gdrnetwork.org
// Never expose these secrets in GitHub Pages/browser code.

import { serve } from 'https://deno.land/std@0.224.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': 'https://www.gdrnetwork.org',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

function template(type: string, payload: any) {
  const site = 'https://www.gdrnetwork.org/'
  if (type === 'idea-submitted') return {
    subject: 'GDR research idea received',
    html: `<h2>Research idea received</h2><p>Your submission <strong>${payload.title || ''}</strong> has been received by GDR.</p><p>It will proceed through scientific screening before any recruitment or public listing.</p><p><a href="${site}">GDR Network</a></p>`
  }
  if (type === 'application-received') return {
    subject: 'GDR collaboration application received',
    html: `<h2>Expression of interest received</h2><p>Your application for ${payload.challenge || 'a GDR Discovery Challenge'} has been received.</p><p>Selection depends on scientific fit, expertise and project requirements.</p>`
  }
  if (type === 'admin-alert') return {
    subject: payload.subject || 'GDR admin notification',
    html: `<h2>GDR Admin Notification</h2><p>${payload.message || 'A new platform event requires review.'}</p>`
  }
  if (type === 'status-update') return {
    subject: 'GDR submission status updated',
    html: `<h2>Status update</h2><p>Your GDR record is now: <strong>${payload.status || 'updated'}</strong>.</p>`
  }
  return { subject: 'GDR notification', html: '<p>You have a new notification from GDR.</p>' }
}

serve(async (req) => {
  if (req.method === 'OPTIONS') return new Response('ok', { headers: corsHeaders })
  try {
    const auth = req.headers.get('Authorization') || ''
    const supabaseUrl = Deno.env.get('SUPABASE_URL')!
    const anon = Deno.env.get('SUPABASE_ANON_KEY')!
    const service = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    const resendKey = Deno.env.get('RESEND_API_KEY')!
    const from = Deno.env.get('GDR_FROM_EMAIL') || 'GDR <notifications@gdrnetwork.org>'
    const adminEmail = Deno.env.get('GDR_ADMIN_EMAIL') || ''

    if (!resendKey) throw new Error('Email provider secret is not configured.')

    const userClient = createClient(supabaseUrl, anon, { global: { headers: { Authorization: auth } } })
    const { data: { user } } = await userClient.auth.getUser()
    if (!user) return new Response(JSON.stringify({ error: 'Authentication required' }), { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })

    const body = await req.json()
    const type = body.type || 'notification'
    let to = body.to || user.email

    // Only founder/admin can send admin-alerts or override recipient.
    if (type === 'admin-alert' || (body.to && body.to !== user.email)) {
      const { data: profile } = await userClient.from('profiles').select('role').eq('user_id', user.id).maybeSingle()
      if (!profile || !['admin','founder'].includes(profile.role)) {
        return new Response(JSON.stringify({ error: 'Founder/Admin role required' }), { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
      }
      if (type === 'admin-alert' && !body.to) to = adminEmail
    }

    if (!to) throw new Error('Recipient email is missing.')
    const content = template(type, body)

    const r = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${resendKey}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ from, to: [to], subject: content.subject, html: content.html })
    })
    const result = await r.json()
    if (!r.ok) throw new Error(result?.message || 'Email provider error')

    const adminClient = createClient(supabaseUrl, service)
    await adminClient.from('email_events').insert({
      event_type: type,
      recipient: to,
      related_entity_type: body.entity_type || null,
      related_entity_id: body.entity_id || null,
      provider_message_id: result.id || null,
      delivery_status: 'sent',
      metadata: { initiated_by: user.id }
    })

    return new Response(JSON.stringify({ ok: true, id: result.id }), { headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  } catch (e) {
    return new Response(JSON.stringify({ error: e.message }), { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } })
  }
})
