#!/bin/bash

# Setup shadcn/ui components
echo "Setting up shadcn/ui components..."

# Initialize shadcn/ui
npx shadcn@latest init --yes

# Install common components
npx shadcn@latest add button
npx shadcn@latest add input
npx shadcn@latest add label
npx shadcn@latest add card
npx shadcn@latest add dialog
npx shadcn@latest add dropdown-menu
npx shadcn@latest add form
npx shadcn@latest add select
npx shadcn@latest add textarea
npx shadcn@latest add toast
npx shadcn@latest add avatar
npx shadcn@latest add badge
npx shadcn@latest add separator
npx shadcn@latest add tabs
npx shadcn@latest add tooltip
npx shadcn@latest add popover
npx shadcn@latest add switch
npx shadcn@latest add checkbox
npx shadcn@latest add alert-dialog

echo "shadcn/ui setup complete!" 