# LogiScore Documentation

This directory contains all documentation for the LogiScore freight forwarder review platform.

## Documentation Files

- **LogiScore Community Guidelines.md** - Community guidelines and standards
- **LogiScore Legal FAQ.md** - Legal frequently asked questions
- **SendGrid-Integration.md** - Email service integration documentation
- **LogiScore Privacy Policy.md** - Privacy policy documentation
- **LogiScore Review Questions.md** - Review question guidelines
- **LogiScore User Requirements.md** - User requirements documentation

## Project Structure

The LogiScore platform consists of:

- **Frontend**: SvelteKit application deployed on Vercel
- **Backend**: FastAPI application deployed on Render
- **Database**: PostgreSQL with Supabase
- **Authentication**: GitHub OAuth with JWT tokens
- **Payment**: Stripe integration for subscriptions

## Development Guidelines

1. All documentation should be kept up to date with code changes
2. Use markdown format for all documentation
3. Include code examples where relevant
4. Maintain consistent formatting and structure

## Deployment

- Frontend: `logiscore-frontend.vercel.app`
- Backend: `logiscore-backend.onrender.com`
- Repository: `https://github.com/LogiScore/frontend` 