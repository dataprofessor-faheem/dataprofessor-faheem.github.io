// GDR shared-backend bridge.
// Public browser code uses only a Supabase publishable key; RLS remains the security boundary.
window.GDRBackend = (() => {
  let client = null;
  const config = () => window.GDR_CONFIG || {};

  async function ensureClient() {
    const c = config();
    if (!c.backendEnabled || !c.supabaseUrl || !c.supabasePublishableKey || !window.supabase) return null;
    if (!client) client = window.supabase.createClient(c.supabaseUrl, c.supabasePublishableKey);
    return client;
  }

  async function getSession() {
    const c = await ensureClient();
    if (!c) return { mode: 'local', session: null };
    const { data, error } = await c.auth.getSession();
    if (error) throw error;
    return { mode: 'shared', session: data.session };
  }

  async function signUp(email, password) {
    const c = await ensureClient();
    if (!c) throw new Error('Shared backend is not configured yet.');
    return c.auth.signUp({ email, password, options: { emailRedirectTo: config().siteUrl + 'gdr/portal/' } });
  }

  async function signIn(email, password) {
    const c = await ensureClient();
    if (!c) throw new Error('Shared backend is not configured yet.');
    return c.auth.signInWithPassword({ email, password });
  }

  async function signOut() {
    const c = await ensureClient();
    if (!c) return;
    return c.auth.signOut();
  }

  async function currentUser() {
    const c = await ensureClient();
    if (!c) return null;
    const { data, error } = await c.auth.getUser();
    if (error) throw error;
    return data.user || null;
  }

  async function getMyProfile() {
    const c = await ensureClient();
    if (!c) return { mode: 'local', profile: null };
    const user = await currentUser();
    if (!user) return { mode: 'shared', profile: null };
    const { data, error } = await c.from('profiles').select('*').eq('user_id', user.id).maybeSingle();
    if (error) throw error;
    return { mode: 'shared', profile: data };
  }

  async function getMyRole() {
    const r = await getMyProfile();
    return r.profile?.role || null;
  }

  function routeForRole(role) {
    if (role === 'founder' || role === 'admin') return '/gdr/admin/';
    if (role === 'manager') return '/gdr/manager/';
    return '/gdr/portal/';
  }

  async function routeSignedInUser() {
    const session = await getSession();
    if (!session.session) return '/gdr/portal/';
    const role = await getMyRole();
    return routeForRole(role);
  }

  async function requireRole(roles) {
    const c = await ensureClient();
    if (!c) throw new Error('Production backend is not connected.');
    const session = await getSession();
    if (!session.session) throw new Error('Please sign in first.');
    const profile = await getMyProfile();
    if (!profile.profile || !roles.includes(profile.profile.role)) throw new Error('Access denied for this account role.');
    return { client: c, session: session.session, profile: profile.profile };
  }

  async function requireAdmin() {
    return requireRole(['founder','admin']);
  }

  async function requireManagerOrAbove() {
    return requireRole(['manager','admin','founder']);
  }

  async function saveProfile(profile) {
    const c = await ensureClient();
    if (!c) return { mode: 'local' };
    const user = await currentUser();
    if (!user) throw new Error('Please sign in first.');
    const row = {
      user_id: user.id,
      full_name: profile.name,
      institution: profile.institution,
      country: profile.country,
      primary_discipline: profile.discipline,
      specializations: profile.specializations,
      methods: profile.methods || null,
      orcid: profile.orcid || null,
      collaboration_interests: profile.interests || null,
      updated_at: new Date().toISOString()
    };
    const { error } = await c.from('profiles').upsert(row, { onConflict: 'user_id' });
    if (error) throw error;
    return { mode: 'shared' };
  }

  async function submitIdea(idea) {
    const c = await ensureClient();
    if (!c) return { mode: 'local' };
    const user = await currentUser();
    if (!user) throw new Error('Please sign in to submit an idea to GDR.');
    const row = {
      submitted_by: user.id,
      title: idea.title,
      primary_domain: idea.domain,
      research_gap: idea.gap,
      multidisciplinary_need: idea.multidisciplinary
    };
    const { data, error } = await c.from('research_ideas').insert(row).select('id').single();
    if (error) throw error;
    return { mode: 'shared', id: data.id };
  }

  async function submitApplication(application) {
    const c = await ensureClient();
    if (!c) return { mode: 'local' };
    const user = await currentUser();
    if (!user) throw new Error('Please sign in to apply for a Discovery Challenge.');
    let challengeId = application.challenge_id || null;
    if (!challengeId && application.challenge_public_id) {
      const { data: ch, error: chErr } = await c.from('discovery_challenges').select('id').eq('public_id', application.challenge_public_id).maybeSingle();
      if (chErr) throw chErr;
      if (!ch) throw new Error('This Discovery Challenge is not registered in the shared database.');
      challengeId = ch.id;
    }
    if (!challengeId) throw new Error('Challenge identifier is missing.');
    const row = {
      challenge_id: challengeId,
      researcher_id: user.id,
      proposed_role: application.proposed_role || application.specialization || 'Research collaborator',
      contribution: application.contribution
    };
    const { data, error } = await c.from('applications').insert(row).select('id').single();
    if (error) throw error;
    return { mode: 'shared', id: data.id };
  }

  async function summaryForOperations() {
    const { client: c } = await requireManagerOrAbove();
    const tables = ['profiles','research_ideas','discovery_challenges','projects','datasets','applications'];
    const out = {};
    for (const table of tables) {
      const { count, error } = await c.from(table).select('*', { count: 'exact', head: true });
      if (error) throw error;
      out[table] = count || 0;
    }
    return out;
  }

  async function adminSummary() {
    await requireAdmin();
    return summaryForOperations();
  }

  async function listIdeas(limit = 100) {
    const { client: c } = await requireManagerOrAbove();
    const { data, error } = await c.from('research_ideas').select('id,title,primary_domain,status,created_at,submitted_by').order('created_at',{ascending:false}).limit(limit);
    if (error) throw error;
    return data || [];
  }

  async function listAdminIdeas(limit = 100) {
    await requireAdmin();
    return listIdeas(limit);
  }

  async function setIdeaStatus(id, status) {
    const { client: c } = await requireManagerOrAbove();
    const { error } = await c.from('research_ideas').update({ status, updated_at: new Date().toISOString() }).eq('id', id);
    if (error) throw error;
    return true;
  }

  async function listResearchers(limit = 200) {
    const { client: c } = await requireManagerOrAbove();
    const { data, error } = await c.from('profiles').select('user_id,full_name,institution,country,primary_discipline,role,verified,created_at').order('created_at',{ascending:false}).limit(limit);
    if (error) throw error;
    return data || [];
  }

  async function listProjects(limit = 200) {
    const { client: c } = await requireManagerOrAbove();
    const { data, error } = await c.from('projects').select('id,project_code,title,status,created_at,updated_at').order('created_at',{ascending:false}).limit(limit);
    if (error) throw error;
    return data || [];
  }

  async function listApplications(limit = 200) {
    const { client: c } = await requireManagerOrAbove();
    const { data, error } = await c.from('applications').select('id,challenge_id,researcher_id,proposed_role,contribution,status,created_at').order('created_at',{ascending:false}).limit(limit);
    if (error) throw error;
    return data || [];
  }

  async function setApplicationStatus(id, status) {
    const { client: c } = await requireManagerOrAbove();
    const { error } = await c.from('applications').update({ status }).eq('id', id);
    if (error) throw error;
    return true;
  }

  async function listChallenges(limit = 100) {
    const { client: c } = await requireManagerOrAbove();
    const { data, error } = await c.from('discovery_challenges').select('id,public_id,title,status,is_public,created_at').order('created_at',{ascending:false}).limit(limit);
    if (error) throw error;
    return data || [];
  }

  async function listDatasets(limit = 200) {
    const { client: c } = await requireManagerOrAbove();
    const { data, error } = await c.from('datasets').select('id,dataset_code,title,access_level,current_version,created_at').order('created_at',{ascending:false}).limit(limit);
    if (error) throw error;
    return data || [];
  }

  async function registerDataset(dataset) {
    const { client: c } = await requireManagerOrAbove();
    const { data, error } = await c.from('datasets').insert(dataset).select('id,dataset_code').single();
    if (error) throw error;
    return data;
  }

  async function registerProject(project) {
    const { client: c } = await requireManagerOrAbove();
    const { data, error } = await c.from('projects').insert(project).select('id,project_code').single();
    if (error) throw error;
    return data;
  }

  async function listAuditEvents(limit = 100) {
    const { client: c } = await requireManagerOrAbove();
    const { data, error } = await c.from('audit_events').select('id,actor_user_id,entity_type,entity_id,action,metadata,created_at').order('created_at',{ascending:false}).limit(limit);
    if (error) throw error;
    return data || [];
  }

  async function sendEmail(type, payload) {
    const c = await ensureClient();
    if (!c) throw new Error('Email service is not active until the backend is connected.');
    const fn = config().emailFunctionName || 'send-gdr-email';
    const { data, error } = await c.functions.invoke(fn, { body: { type, ...payload } });
    if (error) throw error;
    return data;
  }

  return {
    ensureClient, getSession, signUp, signIn, signOut, currentUser,
    saveProfile, getMyProfile, getMyRole, routeForRole, routeSignedInUser,
    requireRole, requireAdmin, requireManagerOrAbove,
    submitIdea, submitApplication, summaryForOperations, adminSummary,
    listIdeas, listAdminIdeas, setIdeaStatus, listResearchers, listProjects,
    listApplications, setApplicationStatus, listChallenges, listDatasets,
    registerDataset, registerProject, listAuditEvents, sendEmail
  };
})();
