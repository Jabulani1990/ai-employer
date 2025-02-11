INSERT INTO ai_workers_aiworker (
    id, 
    name, 
    industry, 
    job_functions, 
    execution_type, 
    default_config, 
    created_at
) VALUES (
    gen_random_uuid(), 
    'AI Property Manager', 
    'Real Estate', 
    '["Property Listing", "Rent Collection", "Tenant Communication", "Maintenance Scheduling"]', 
    'hybrid', 
    '{"auto_reminders": true, "report_frequency": "weekly"}', 
    NOW()
);



-- Property Management Tasks
INSERT INTO ai_workers_aitask (name, description, execution_type, status, priority, created_at, updated_at, assigned_ai_worker_id)
VALUES 
('Auto-generate property listings', 'Automatically generate and format property listings based on property data', 'fully_autonomous', 'pending', 'medium', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Sync listings to platforms', 'Synchronize property listings across multiple real estate platforms', 'fully_autonomous', 'pending', 'medium', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Price recommendations', 'Generate pricing recommendations based on market analysis', 'hybrid', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Track available & occupied properties', 'Monitor and update property availability status', 'fully_autonomous', 'pending', 'medium', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Update listings (sold/rented)', 'Automatically update listing status when properties are sold or rented', 'fully_autonomous', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager'));

-- Tenant & Lease Management Tasks
INSERT INTO ai_workers_aitask (name, description, execution_type, status, priority, created_at, updated_at, assigned_ai_worker_id)
VALUES 
('Screen tenant applications', 'Process and evaluate tenant applications based on predefined criteria', 'rule_based', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Generate lease agreements', 'Create customized lease agreements based on property and tenant information', 'hybrid', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Send lease renewal reminders', 'Automatically send reminders for upcoming lease renewals', 'fully_autonomous', 'pending', 'medium', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Handle rent collection notifications', 'Send automated rent collection notifications to tenants', 'fully_autonomous', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Automate eviction notices', 'Generate and manage eviction notices with human oversight', 'hybrid', 'pending', 'critical', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager'));

-- Payment & Financial Management Tasks
INSERT INTO ai_workers_aitask (name, description, execution_type, status, priority, created_at, updated_at, assigned_ai_worker_id)
VALUES 
('Send rental payment reminders', 'Send automated payment reminders to tenants', 'fully_autonomous', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Track rent payments & balances', 'Monitor and record rent payments and maintain balance sheets', 'fully_autonomous', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Auto-generate financial reports', 'Generate comprehensive financial reports and analytics', 'fully_autonomous', 'pending', 'medium', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Detect overdue payments', 'Identify and flag overdue rental payments', 'fully_autonomous', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Issue late fee notices', 'Generate and send late fee notices based on payment rules', 'rule_based', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager'));

-- Maintenance & Repairs Tasks
INSERT INTO ai_workers_aitask (name, description, execution_type, status, priority, created_at, updated_at, assigned_ai_worker_id)
VALUES 
('Accept repair requests via chatbot', 'Process maintenance requests through AI chatbot interface', 'fully_autonomous', 'pending', 'medium', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Match repair requests with vendors', 'Automatically match maintenance requests with appropriate vendors', 'rule_based', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Auto-schedule maintenance tasks', 'Schedule routine maintenance tasks and inspections', 'fully_autonomous', 'pending', 'medium', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Generate work orders', 'Create and manage work orders for maintenance tasks', 'hybrid', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager'));

-- Market Insights & Strategy Tasks
INSERT INTO ai_workers_aitask (name, description, execution_type, status, priority, created_at, updated_at, assigned_ai_worker_id)
VALUES 
('Track property market trends', 'Monitor and analyze real estate market trends', 'fully_autonomous', 'pending', 'medium', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Competitor pricing analysis', 'Analyze competitor property prices and market positioning', 'fully_autonomous', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Investment recommendations', 'Generate property investment recommendations with human approval', 'hybrid', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager'));

-- Customer Support & Engagement Tasks
INSERT INTO ai_workers_aitask (name, description, execution_type, status, priority, created_at, updated_at, assigned_ai_worker_id)
VALUES 
('Answer FAQs via chatbot', 'Provide automated responses to common customer inquiries', 'fully_autonomous', 'pending', 'medium', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Automate tenant inquiries', 'Process and respond to tenant queries automatically', 'fully_autonomous', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Follow-up with leads', 'Automated follow-up communication with potential clients', 'rule_based', 'pending', 'high', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager')),
('Send personalized property promotions', 'Generate and send targeted property promotional content', 'rule_based', 'pending', 'medium', NOW(), NOW(), (SELECT id FROM ai_workers_aiworker WHERE name = 'AI Property Manager'));
