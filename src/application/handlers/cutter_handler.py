"""
Command and Query Handlers - Application Service Layer.

Handlers orchestrate the execution of commands and queries by:
1. Validating input
2. Interacting with domain services and repositories
3. Returning DTOs or results

Following the Handler pattern for clean separation of concerns.
"""

from typing import Optional
from uuid import UUID

from src.domain.models.cutter import Cutter, CutterType, MaterialSpec, GeometryParams
from src.domain.repositories.cutter_repo import (
    CutterRepository,
    DuplicateCutterError,
    CutterNotFoundError,
)
from src.application.commands.ingest_cutter import IngestCutterCommand, UpdateCutterCommand
from src.application.queries.search_cutters import (
    SearchCuttersQuery,
    GetCutterByIdQuery,
    GetAllCuttersQuery,
    SearchByMaterialQuery,
)
from src.application.dto.cutter_dto import CutterDTO, CutterSearchResultDTO


class CutterCommandHandler:
    """
    Handler for cutter-related commands.
    
    This class implements the application service layer:
    - Coordinates repository operations
    - Enforces business rules
    - Transforms domain models to DTOs
    
    Design Patterns used:
    - Command Handler: Centralizes command execution logic
    - Dependency Injection: Repository injected via constructor
    """
    
    def __init__(self, repository: CutterRepository) -> None:
        self._repository = repository
    
    def handle_ingest(self, command: IngestCutterCommand) -> CutterDTO:
        """
        Execute an IngestCutterCommand.
        
        Args:
            command: The command containing cutter data
            
        Returns:
            CutterDTO of the created cutter
            
        Raises:
            ValueError: If command validation fails
            DuplicateCutterError: If cutter already exists
        """
        # Step 1: Validate command
        errors = command.validate()
        if errors:
            raise ValueError(f"Command validation failed: {', '.join(errors)}")
        
        # Step 2: Build value objects
        cutter_type = CutterType(
            category=command.category,
            subcategory=command.subcategory,
            coating=command.coating,
        )
        
        material = MaterialSpec(
            substrate=command.substrate,
            coating_type=command.coating_type,
            hardness_hrc=command.hardness_hrc,
        )
        
        geometry = GeometryParams(
            diameter=command.diameter,
            length=command.length,
            flute_length=command.flute_length,
            number_of_flutes=command.number_of_flutes,
            helix_angle=command.helix_angle,
            corner_radius=command.corner_radius,
        )
        
        # Step 3: Create domain aggregate using factory method
        cutter = Cutter.create(
            name=command.name,
            cutter_type=cutter_type,
            material=material,
            geometry=geometry,
            recommended_parameters=command.recommended_parameters,
            usage_guidelines=command.usage_guidelines,
            compatible_materials=command.compatible_materials,
            cutter_id=command.cutter_id,
        )
        
        # Step 4: Persist via repository
        self._repository.add(cutter)
        
        # Step 5: Return DTO
        return CutterDTO.from_domain(cutter)
    
    def handle_update(self, command: UpdateCutterCommand) -> CutterDTO:
        """
        Execute an UpdateCutterCommand.
        
        Args:
            command: The update command
            
        Returns:
            CutterDTO of the updated cutter
            
        Raises:
            CutterNotFoundError: If cutter doesn't exist
        """
        # Retrieve existing cutter
        cutter = self._repository.get_by_id(command.cutter_id)
        if not cutter:
            raise CutterNotFoundError(f"Cutter {command.cutter_id} not found")
        
        # Apply updates (demonstrates entity mutability)
        if command.name:
            cutter.name = command.name
        
        if command.usage_guidelines:
            cutter.usage_guidelines = command.usage_guidelines
        
        if command.compatible_materials:
            cutter.compatible_materials = command.compatible_materials
        
        if command.recommended_parameters:
            cutter.recommended_parameters.update(command.recommended_parameters)
        
        # Persist changes
        self._repository.update(cutter)
        
        return CutterDTO.from_domain(cutter)
    
    def handle_delete(self, cutter_id: UUID) -> bool:
        """
        Delete a cutter by ID.
        
        Args:
            cutter_id: The unique identifier
            
        Returns:
            True if deleted, False if not found
        """
        return self._repository.delete(cutter_id)


class CutterQueryHandler:
    """
    Handler for cutter-related queries.
    
    Following CQRS principles, read operations are separated from write operations.
    This handler is optimized for read scenarios.
    """
    
    def __init__(self, repository: CutterRepository) -> None:
        self._repository = repository
    
    def handle_search(self, query: SearchCuttersQuery) -> list[CutterSearchResultDTO]:
        """
        Execute a semantic search query.
        
        Args:
            query: Search parameters
            
        Returns:
            List of search results with relevance scores
        """
        results = self._repository.search_by_query(
            query=query.query_text,
            top_k=query.top_k,
            filters=query.filters,
        )
        
        return [
            CutterSearchResultDTO(
                cutter=CutterDTO.from_domain(cutter),
                relevance_score=score,
            )
            for cutter, score in results
        ]
    
    def handle_get_by_id(self, query: GetCutterByIdQuery) -> Optional[CutterDTO]:
        """
        Retrieve a single cutter by ID.
        
        Args:
            query: Query with cutter ID
            
        Returns:
            CutterDTO if found, None otherwise
        """
        try:
            cutter_id = UUID(query.cutter_id)
        except ValueError:
            return None
        
        cutter = self._repository.get_by_id(cutter_id)
        if not cutter:
            return None
        
        return CutterDTO.from_domain(cutter)
    
    def handle_get_all(self, query: GetAllCuttersQuery) -> list[CutterDTO]:
        """
        Retrieve all cutters with pagination.
        
        Args:
            query: Pagination parameters
            
        Returns:
            List of CutterDTOs
        """
        all_cutters = self._repository.get_all()
        paginated = all_cutters[query.offset : query.offset + query.limit]
        return [CutterDTO.from_domain(c) for c in paginated]
    
    def handle_search_by_material(
        self, 
        query: SearchByMaterialQuery,
    ) -> list[CutterDTO]:
        """
        Find cutters suitable for a workpiece material.
        
        Args:
            query: Material search parameters
            
        Returns:
            List of compatible CutterDTOs
        """
        cutters = self._repository.search_by_material(
            workpiece_material=query.workpiece_material,
            top_k=query.top_k,
        )
        return [CutterDTO.from_domain(c) for c in cutters]
