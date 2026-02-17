# Auto di Cortesia Implementation Summary

## Overview
Complete implementation of the "Auto di Cortesia" (Courtesy Car) feature for the Garage Management System. This feature allows tracking and managing the availability state of courtesy vehicles provided to customers.

## Architecture & Design

### Business Logic
- **Courtesy cars** are vehicles registered with an `auto_cortesia_stato` field
- State management through a system lookup table (`auto_cortesia_stati`)
- Predefined states: `disponibile`, `in_uso`, `manutenzione`, `non_disponibile`
- Read-only state display in work order form (editing via vehicle management)
- Currently designed for integration with customer vehicles (future enhancement)

### Database Schema

#### New Table: `auto_cortesia_stati`
```sql
CREATE TABLE auto_cortesia_stati (
  id INTEGER PRIMARY KEY,
  nome VARCHAR(50) UNIQUE NOT NULL,
  descrizione VARCHAR(255),
  attivo BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

**Initial States:**
- `disponibile` - Vehicle is available for assignment/rental
- `in_uso` - Vehicle is currently assigned to a customer
- `manutenzione` - Vehicle is undergoing maintenance
- `non_disponibile` - Vehicle is not available for assignment

#### Vehicle Table Updates
Added column to existing `veicoli` table:
```sql
auto_cortesia_stato VARCHAR(50) -- nullable, references auto_cortesia_stati.nome
```

## Backend Implementation

### 1. Database Models

#### `system_tables.py` - `AutoCortesiaStato` Model
```python
class AutoCortesiaStato(Base):
    __tablename__ = "auto_cortesia_stati"
    
    id = Column(Integer, primary_key=True)
    nome = Column(String(50), unique=True, nullable=False)
    descrizione = Column(String(255), nullable=True)
    attivo = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

#### `vehicle.py` - Updated Vehicle Model
```python
auto_cortesia_stato = Column(String(50), nullable=True)
```

### 2. API Schemas (`schemas/system_tables.py`)

**Request Schemas:**
- `AutoCortesiaStatoCreate` - Create new state
- `AutoCortesiaStatoUpdate` - Update existing state

**Response Schema:**
- `AutoCortesiaStatoResponse` - Standard response with all fields

### 3. API Endpoints (`api/v1/endpoints/system_tables.py`)

#### Available Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/system-tables/auto-cortesia-stati` | List active states | Authenticated |
| GET | `/system-tables/auto-cortesia-stati/all` | List all states (inactive included) | Admin Only |
| POST | `/system-tables/auto-cortesia-stati` | Create new state | Admin Only |
| PUT | `/system-tables/auto-cortesia-stati/{id}` | Update state | Admin Only |
| DELETE | `/system-tables/auto-cortesia-stati/{id}` | Delete state | Admin Only |

**Features:**
- Automatic uniqueness validation on `nome` field
- Active/inactive state management
- CRUD operations with proper error handling
- Timestamps for audit trail

### 4. Database Migration

**File:** `alembic/versions/20260217_0001-auto_cortesia_support.py`

**Operations:**
1. Creates `auto_cortesia_stati` table with initial states
2. Adds `auto_cortesia_stato` column to `veicoli` table
3. Includes upgrade/downgrade support for rollback capability

**Usage:**
```bash
# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

## Frontend Implementation

### 1. Types & Enums (`src/types/index.ts`)

```typescript
export enum AutoCortesiaStato {
  DISPONIBILE = 'disponibile',
  IN_USO = 'in_uso',
  MANUTENZIONE = 'manutenzione',
  NON_DISPONIBILE = 'non_disponibile',
}

export interface AutoCortesiaStatoResponse {
  id: number
  nome: string
  descrizione?: string
  attivo: boolean
  created_at: string
  updated_at?: string
}
```

Updated `Vehicle` interface:
```typescript
interface Vehicle {
  // ... existing fields
  auto_cortesia_stato?: string  // State of courtesy car availability
}
```

### 2. API Configuration (`src/config/api.ts`)

Added endpoint:
```typescript
SYSTEM_AUTO_CORTESIA_STATI: '/system-tables/auto-cortesia-stati'
```

### 3. Custom Hook (`src/hooks/useSystemTables.ts`)

```typescript
export const useAutoCortesiaStati = () => {
  return useQuery({
    queryKey: ['auto-cortesia-stati'],
    queryFn: async () => {
      const response = await axiosInstance.get<SystemTableItem[]>(
        API_ENDPOINTS.SYSTEM_AUTO_CORTESIA_STATI
      )
      return response.data || []
    },
    staleTime: 1000 * 60 * 5,    // 5 minutes
    gcTime: 1000 * 60 * 10,      // 10 minutes
  })
}
```

### 4. Work Order Form Integration

**Tab 4: "Auto di Cortesia"** in `WorkOrdersPage.tsx`

**Features:**
- Displays courtesy car information when vehicle is registered as courtesy car
- Read-only state display with color-coded tags
- Vehicle details: targa, marca/modello, year
- State explanation tooltips
- Admin link for state management
- Graceful fallback when vehicle is not a courtesy car

**States Supported:**
- **✅ Active State:** Show vehicle info, current state, and state descriptions
- **⚠️ Inactive State:** Display message suggesting admin contact for registration

**UI Components:**
- Info card showing vehicle details
- Color-coded state tag (blue)
- Informational box explaining state meanings
- Warning box for non-courtesy vehicles

## Integration Points

### 1. Work Order Display
- When editing a work order, Tab 4 automatically detects if vehicle has `auto_cortesia_stato`
- Shows state information in read-only format
- Provides context about future rental/assignment capabilities

### 2. Vehicle Management
- Future: Add courtesy car settings to vehicle details page
- Allow toggling vehicle as courtesy car
- Enable state transitions through dedicated UI

### 3. Customer Assignment
- Future: Link work orders to auto di cortesia assignments
- Track vehicle rentals and returns
- Generate rental reports

## Future Enhancements

### Phase 2: Advanced Features
1. **Auto di Cortesia Assignment System**
   - Create `car_assignments` table for tracking rentals
   - Link work orders to courtesy car assignments
   - Track pickup/return dates and km

2. **State Transition Workflows**
   - Automated status updates based on work order state
   - Validation rules for state transitions
   - Notification system for state changes

3. **Rental Management**
   - Rental contracts and agreements
   - Cost tracking and invoicing
   - Customer rental history

4. **Admin Dashboard**
   - Courtesy car availability overview
   - Rental calendar
   - Maintenance scheduling
   - Revenue reports

### Phase 3: Analytics
- Fleet utilization metrics
- Revenue analysis by courtesy car
- Maintenance cost tracking
- Customer rental patterns

## Testing Checklist

- [ ] Database migration applies successfully
- [ ] Backend API endpoints return correct data
- [ ] Frontend hook fetches states correctly
- [ ] Work order form displays courtesy car tab
- [ ] State display works for both courtesy and non-courtesy vehicles
- [ ] Admin can manage states through admin panel (future)
- [ ] Permission checks work correctly
- [ ] Error handling for missing/invalid states

## Troubleshooting

### Common Issues

**Issue:** `AutoCortesiaStato` model not imported
- **Solution:** Ensure `app/models/__init__.py` includes the import

**Issue:** API endpoint returns 404
- **Solution:** Verify migration has been applied: `alembic upgrade head`

**Issue:** Frontend tab shows no states
- **Solution:** Check network tab in dev tools, verify backend returns data

**Issue:** Vehicle state not displaying
- **Solution:** Verify vehicle record has `auto_cortesia_stato` value set

## Files Modified/Created

### Backend
- ✅ `app/models/vehicle.py` - Added `auto_cortesia_stato` column
- ✅ `app/models/system_tables.py` - Added `AutoCortesiaStato` class
- ✅ `app/models/__init__.py` - Exported `AutoCortesiaStato`
- ✅ `app/schemas/system_tables.py` - Added schemas for CRUD operations
- ✅ `app/api/v1/endpoints/system_tables.py` - Added endpoints
- ✅ `alembic/versions/20260217_0001-auto_cortesia_support.py` - Database migration

### Frontend
- ✅ `src/types/index.ts` - Added `AutoCortesiaStato` enum and `AutoCortesiaStatoResponse` interface
- ✅ `src/config/api.ts` - Added API endpoint configuration
- ✅ `src/hooks/useSystemTables.ts` - Added `useAutoCortesiaStati` hook
- ✅ `src/pages/work-orders/WorkOrdersPage.tsx` - Implemented Tab 4 UI

## API Response Examples

### GET /system-tables/auto-cortesia-stati

**Success Response (200):**
```json
[
  {
    "id": 1,
    "nome": "disponibile",
    "descrizione": null,
    "attivo": true,
    "created_at": "2025-02-17T10:00:00",
    "updated_at": "2025-02-17T10:00:00"
  },
  {
    "id": 2,
    "nome": "in_uso",
    "descrizione": "Auto assegnata a un cliente",
    "attivo": true,
    "created_at": "2025-02-17T10:00:00",
    "updated_at": "2025-02-17T10:00:00"
  },
  {
    "id": 3,
    "nome": "manutenzione",
    "descrizione": null,
    "attivo": true,
    "created_at": "2025-02-17T10:00:00",
    "updated_at": "2025-02-17T10:00:00"
  },
  {
    "id": 4,
    "nome": "non_disponibile",
    "descrizione": null,
    "attivo": true,
    "created_at": "2025-02-17T10:00:00",
    "updated_at": "2025-02-17T10:00:00"
  }
]
```

### POST /system-tables/auto-cortesia-stati

**Request:**
```json
{
  "nome": "in_revisione",
  "descrizione": "Auto in revisione tecnica"
}
```

**Response (201):**
```json
{
  "id": 5,
  "nome": "in_revisione",
  "descrizione": "Auto in revisione tecnica",
  "attivo": true,
  "created_at": "2025-02-17T11:30:00",
  "updated_at": "2025-02-17T11:30:00"
}
```

## Deployment Notes

1. **Database Migration:** Must be applied before deploying code changes
2. **Backward Compatibility:** Non-courtesy vehicles will have `null` auto_cortesia_stato
3. **Feature Flag:** Consider adding feature flag for courtesy car management in Phase 2
4. **Caching:** Frontend hook caches states for 5 minutes; invalidate after admin updates

## Performance Considerations

- States cached on frontend (5 min TTL)
- Vehicle queries may need index on `auto_cortesia_stato` if dataset grows large
- Consider denormalizing vehicle-to-state relationship at scale
- API response is minimal (4 base states) - no pagination needed

## Security

- ✅ All endpoints require authentication
- ✅ Admin-only endpoints for state management
- ✅ Input validation on state names (50 char max)
- ✅ Unique constraint on state names prevents duplicates
- ✅ Soft delete approach (attivo field) for state deactivation

