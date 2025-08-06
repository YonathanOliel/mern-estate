-- LegalGPT Enterprise Database Schema
-- PostgreSQL 15+ with advanced features

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";
CREATE EXTENSION IF NOT EXISTS "vector";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create custom types
CREATE TYPE user_role AS ENUM ('user', 'premium', 'lawyer', 'admin', 'super_admin');
CREATE TYPE subscription_plan AS ENUM ('free', 'basic', 'premium', 'enterprise');
CREATE TYPE document_status AS ENUM ('draft', 'generating', 'completed', 'failed', 'archived');
CREATE TYPE chat_session_status AS ENUM ('active', 'completed', 'archived');
CREATE TYPE payment_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'refunded');

-- Users table with advanced features
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    role user_role DEFAULT 'user',
    subscription_plan subscription_plan DEFAULT 'free',
    subscription_expires_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    verification_token VARCHAR(255),
    reset_password_token VARCHAR(255),
    reset_password_expires TIMESTAMP WITH TIME ZONE,
    last_login_at TIMESTAMP WITH TIME ZONE,
    login_attempts INTEGER DEFAULT 0,
    locked_until TIMESTAMP WITH TIME ZONE,
    preferences JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- User sessions for JWT token management
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash VARCHAR(255) NOT NULL,
    device_info JSONB,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_used_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Legal categories with hierarchical structure
CREATE TABLE legal_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    name_he VARCHAR(100) NOT NULL,
    description TEXT,
    description_he TEXT,
    parent_id UUID REFERENCES legal_categories(id),
    icon VARCHAR(50),
    color VARCHAR(7),
    keywords TEXT[],
    keywords_he TEXT[],
    is_active BOOLEAN DEFAULT true,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat sessions with advanced tracking
CREATE TABLE chat_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    category_id UUID REFERENCES legal_categories(id),
    title VARCHAR(255),
    status chat_session_status DEFAULT 'active',
    language VARCHAR(5) DEFAULT 'he',
    context JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    total_messages INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 4) DEFAULT 0,
    satisfaction_rating INTEGER CHECK (satisfaction_rating >= 1 AND satisfaction_rating <= 5),
    feedback TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Chat messages with vector embeddings for semantic search
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    content_tokens INTEGER,
    embedding vector(1536), -- OpenAI ada-002 embeddings
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Document templates with version control
CREATE TABLE document_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    name_he VARCHAR(100) NOT NULL,
    description TEXT,
    description_he TEXT,
    category_id UUID REFERENCES legal_categories(id),
    template_content TEXT NOT NULL,
    template_variables JSONB DEFAULT '{}',
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT true,
    requires_subscription subscription_plan DEFAULT 'free',
    preview_url VARCHAR(500),
    tags TEXT[],
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Generated documents with full tracking
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id UUID REFERENCES chat_sessions(id) ON DELETE SET NULL,
    template_id UUID REFERENCES document_templates(id),
    title VARCHAR(255) NOT NULL,
    format VARCHAR(10) NOT NULL CHECK (format IN ('pdf', 'docx', 'html')),
    status document_status DEFAULT 'draft',
    content_data JSONB,
    file_path VARCHAR(500),
    file_size BIGINT,
    download_count INTEGER DEFAULT 0,
    is_public BOOLEAN DEFAULT false,
    expires_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Payment transactions
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_payment_intent_id VARCHAR(255) UNIQUE,
    amount_cents INTEGER NOT NULL,
    currency VARCHAR(3) DEFAULT 'ILS',
    status payment_status DEFAULT 'pending',
    description TEXT,
    metadata JSONB DEFAULT '{}',
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Subscription history
CREATE TABLE subscriptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    plan subscription_plan NOT NULL,
    stripe_subscription_id VARCHAR(255),
    status VARCHAR(50) NOT NULL,
    current_period_start TIMESTAMP WITH TIME ZONE,
    current_period_end TIMESTAMP WITH TIME ZONE,
    canceled_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Analytics events for tracking user behavior
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    session_id VARCHAR(255),
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB DEFAULT '{}',
    ip_address INET,
    user_agent TEXT,
    referrer TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- API usage tracking
CREATE TABLE api_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    endpoint VARCHAR(255) NOT NULL,
    method VARCHAR(10) NOT NULL,
    status_code INTEGER NOT NULL,
    response_time_ms INTEGER,
    tokens_used INTEGER DEFAULT 0,
    cost_usd DECIMAL(10, 6) DEFAULT 0,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- System notifications
CREATE TABLE notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    data JSONB DEFAULT '{}',
    is_read BOOLEAN DEFAULT false,
    read_at TIMESTAMP WITH TIME ZONE,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Audit log for compliance
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_subscription ON users(subscription_plan);
CREATE INDEX idx_users_active ON users(is_active) WHERE is_active = true;
CREATE INDEX idx_users_created_at ON users(created_at);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
CREATE INDEX idx_user_sessions_refresh_token ON user_sessions(refresh_token_hash);

CREATE INDEX idx_legal_categories_parent ON legal_categories(parent_id);
CREATE INDEX idx_legal_categories_active ON legal_categories(is_active) WHERE is_active = true;
CREATE INDEX idx_legal_categories_keywords ON legal_categories USING GIN(keywords);
CREATE INDEX idx_legal_categories_keywords_he ON legal_categories USING GIN(keywords_he);

CREATE INDEX idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX idx_chat_sessions_category_id ON chat_sessions(category_id);
CREATE INDEX idx_chat_sessions_status ON chat_sessions(status);
CREATE INDEX idx_chat_sessions_created_at ON chat_sessions(created_at);

CREATE INDEX idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX idx_chat_messages_created_at ON chat_messages(created_at);
CREATE INDEX idx_chat_messages_embedding ON chat_messages USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_session_id ON documents(session_id);
CREATE INDEX idx_documents_template_id ON documents(template_id);
CREATE INDEX idx_documents_status ON documents(status);
CREATE INDEX idx_documents_created_at ON documents(created_at);

CREATE INDEX idx_payments_user_id ON payments(user_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_stripe_id ON payments(stripe_payment_intent_id);
CREATE INDEX idx_payments_created_at ON payments(created_at);

CREATE INDEX idx_analytics_events_user_id ON analytics_events(user_id);
CREATE INDEX idx_analytics_events_type ON analytics_events(event_type);
CREATE INDEX idx_analytics_events_created_at ON analytics_events(created_at);

CREATE INDEX idx_api_usage_user_id ON api_usage(user_id);
CREATE INDEX idx_api_usage_endpoint ON api_usage(endpoint);
CREATE INDEX idx_api_usage_created_at ON api_usage(created_at);

CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = false;

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);

-- Full-text search indexes
CREATE INDEX idx_chat_messages_content_fts ON chat_messages USING GIN(to_tsvector('hebrew', content));
CREATE INDEX idx_documents_title_fts ON documents USING GIN(to_tsvector('hebrew', title));

-- Create triggers for updated_at timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_legal_categories_updated_at BEFORE UPDATE ON legal_categories
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chat_sessions_updated_at BEFORE UPDATE ON chat_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_document_templates_updated_at BEFORE UPDATE ON document_templates
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at BEFORE UPDATE ON payments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON subscriptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create audit trigger function
CREATE OR REPLACE FUNCTION audit_trigger_function()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO audit_logs (action, resource_type, resource_id, new_values, user_id)
        VALUES (TG_OP, TG_TABLE_NAME, NEW.id, row_to_json(NEW), 
                COALESCE(NEW.user_id, (current_setting('app.current_user_id', true))::UUID));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO audit_logs (action, resource_type, resource_id, old_values, new_values, user_id)
        VALUES (TG_OP, TG_TABLE_NAME, NEW.id, row_to_json(OLD), row_to_json(NEW),
                COALESCE(NEW.user_id, (current_setting('app.current_user_id', true))::UUID));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO audit_logs (action, resource_type, resource_id, old_values, user_id)
        VALUES (TG_OP, TG_TABLE_NAME, OLD.id, row_to_json(OLD),
                COALESCE(OLD.user_id, (current_setting('app.current_user_id', true))::UUID));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Apply audit triggers to critical tables
CREATE TRIGGER audit_users AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_payments AFTER INSERT OR UPDATE OR DELETE ON payments
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

CREATE TRIGGER audit_documents AFTER INSERT OR UPDATE OR DELETE ON documents
    FOR EACH ROW EXECUTE FUNCTION audit_trigger_function();

-- Insert default legal categories
INSERT INTO legal_categories (name, name_he, description, description_he, keywords, keywords_he, icon, color, sort_order) VALUES
('Employment Law', 'דיני עבודה', 'Employment rights, termination, wages', 'זכויות עובדים, פיטורין, שכר', 
 ARRAY['employment', 'termination', 'salary', 'workplace'], 
 ARRAY['עבודה', 'פיטורין', 'שכר', 'מקום עבודה'], 'work', '#1976d2', 1),

('Rental Law', 'דיני שכירות', 'Tenant rights, lease agreements, evictions', 'זכויות שוכרים, חוזי שכירות, פינוי',
 ARRAY['rental', 'lease', 'tenant', 'landlord', 'eviction'],
 ARRAY['שכירות', 'חוזה', 'שוכר', 'משכיר', 'פינוי'], 'home', '#388e3c', 2),

('Consumer Rights', 'זכויות צרכן', 'Product defects, refunds, warranties', 'פגמים במוצר, החזרים, אחריות',
 ARRAY['consumer', 'defect', 'warranty', 'refund', 'purchase'],
 ARRAY['צרכן', 'פגם', 'אחריות', 'החזר', 'רכישה'], 'shopping_cart', '#f57c00', 3),

('Family Law', 'דיני משפחה', 'Divorce, custody, alimony, inheritance', 'גירושין, משמורת, מזונות, ירושה',
 ARRAY['divorce', 'custody', 'alimony', 'inheritance', 'marriage'],
 ARRAY['גירושין', 'משמורת', 'מזונות', 'ירושה', 'נישואין'], 'family_restroom', '#e91e63', 4),

('Small Claims', 'תביעות קטנות', 'Small monetary disputes, debt collection', 'סכסוכים כספיים קטנים, גביית חובות',
 ARRAY['small claims', 'debt', 'money', 'dispute', 'court'],
 ARRAY['תביעה קטנה', 'חוב', 'כסף', 'סכסוך', 'בית משפט'], 'gavel', '#9c27b0', 5),

('Real Estate', 'נדל"ן', 'Property transactions, construction defects', 'עסקאות נדל"ן, פגמי בנייה',
 ARRAY['real estate', 'property', 'construction', 'defects', 'purchase'],
 ARRAY['נדלן', 'נכס', 'בנייה', 'פגמים', 'רכישה'], 'location_city', '#607d8b', 6);

-- Create database views for common queries
CREATE VIEW user_stats AS
SELECT 
    u.id,
    u.email,
    u.subscription_plan,
    COUNT(DISTINCT cs.id) as total_sessions,
    COUNT(DISTINCT d.id) as total_documents,
    SUM(cs.total_tokens) as total_tokens_used,
    SUM(cs.cost_usd) as total_cost_usd,
    u.created_at,
    u.last_login_at
FROM users u
LEFT JOIN chat_sessions cs ON u.id = cs.user_id
LEFT JOIN documents d ON u.id = d.user_id
GROUP BY u.id, u.email, u.subscription_plan, u.created_at, u.last_login_at;

CREATE VIEW popular_templates AS
SELECT 
    dt.id,
    dt.name,
    dt.name_he,
    lc.name as category_name,
    lc.name_he as category_name_he,
    COUNT(d.id) as usage_count,
    dt.created_at
FROM document_templates dt
LEFT JOIN legal_categories lc ON dt.category_id = lc.id
LEFT JOIN documents d ON dt.id = d.template_id
WHERE dt.is_active = true
GROUP BY dt.id, dt.name, dt.name_he, lc.name, lc.name_he, dt.created_at
ORDER BY usage_count DESC;

-- Grant permissions (adjust based on your user setup)
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO legalgpt_user;
-- GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO legalgpt_user;
-- GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO legalgpt_user;